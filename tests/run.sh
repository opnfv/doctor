#!/bin/bash -e
##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Configuration

[[ "${CI_DEBUG:-true}" == [Tt]rue ]] && set -x

IMAGE_URL=https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
#if an existing image name is provided in the enviroment, use that one
IMAGE_NAME=${IMAGE_NAME:-cirros}
IMAGE_FILE="${IMAGE_NAME}.img"
IMAGE_FORMAT=qcow2
VM_NAME=doctor_vm1
VM_FLAVOR=m1.tiny
ALARM_NAME=doctor_alarm1
INSPECTOR_PORT=12345
CONSUMER_PORT=12346
DOCTOR_USER=doctor
DOCTOR_PW=doctor
DOCTOR_PROJECT=doctor
#TODO: change back to `_member_` when JIRA DOCTOR-55 is done
DOCTOR_ROLE=admin
PROFILER_TYPE=${PROFILER_TYPE:-none}

TOP_DIR=$(cd $(dirname "$0") && pwd)

as_doctor_user="--os-username $DOCTOR_USER --os-password $DOCTOR_PW
                --os-tenant-name $DOCTOR_PROJECT"


# Functions

get_compute_host_info() {
    # get computer host info which VM boot in
    COMPUTE_HOST=$(openstack $as_doctor_user server show $VM_NAME |
                   grep "OS-EXT-SRV-ATTR:host" | awk '{ print $4 }')
    compute_host_in_undercloud=${COMPUTE_HOST%%.*}
    die_if_not_set $LINENO COMPUTE_HOST "Failed to get compute hostname"

    get_compute_ip_from_hostname $COMPUTE_HOST

    echo "COMPUTE_HOST=$COMPUTE_HOST"
    echo "COMPUTE_IP=$COMPUTE_IP"

    # verify connectivity to target compute host
    ping -c 1 "$COMPUTE_IP"
    if [[ $? -ne 0 ]] ; then
        die $LINENO "Can not ping to computer host"
    fi

    # verify ssh to target compute host
    ssh $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP" 'exit'
    if [[ $? -ne 0 ]] ; then
        die $LINENO "Can not ssh to computer host"
    fi
}

# TODO(r-mibu): update this function to support consumer instance
#               and migrate this function into installer lib
get_consumer_ip___to_be_removed() {
    local get_consumer_command="ip route get $COMPUTE_IP | awk '/ src /{print \$NF}'"
    if is_installer apex; then
        CONSUMER_IP=$(sudo ssh $ssh_opts root@$INSTALLER_IP \
                      "$get_consumer_command")
    elif is_installer fuel; then
        CONSUMER_IP=$(sudo sshpass -p r00tme ssh $ssh_opts root@${INSTALLER_IP} \
                      "$get_consumer_command")
    elif is_installer local; then
        CONSUMER_IP=`$get_consumer_command`
    fi
    echo "CONSUMER_IP=$CONSUMER_IP"

    die_if_not_set $LINENO CONSUMER_IP "Could not get CONSUMER_IP."
}

download_image() {
    #if a different name was provided for the image in the enviroment there's no need to download the image
    use_existing_image=false
    openstack image list | grep -q " $IMAGE_NAME " && use_existing_image=true

    if [[ "$use_existing_image" == false ]] ; then
        [ -e "$IMAGE_FILE" ] && return 0
        wget "$IMAGE_URL" -o "$IMAGE_FILE"
    fi
}

register_image() {
    openstack image list | grep -q " $IMAGE_NAME " && return 0
    openstack image create "$IMAGE_NAME" \
                           --public \
                           --disk-format "$IMAGE_FORMAT" \
                           --container-format bare \
                           --file "$IMAGE_FILE"
}

create_test_user() {
    openstack project list | grep -q " $DOCTOR_PROJECT " || {
        openstack project create "$DOCTOR_PROJECT"
    }
    openstack user list | grep -q " $DOCTOR_USER " || {
        openstack user create "$DOCTOR_USER" --password "$DOCTOR_PW" \
                              --project "$DOCTOR_PROJECT"
    }
    openstack user role list "$DOCTOR_USER" --project "$DOCTOR_PROJECT" \
    | grep -q " $DOCTOR_ROLE " || {
        openstack role add "$DOCTOR_ROLE" --user "$DOCTOR_USER" \
                           --project "$DOCTOR_PROJECT"
    }
}

boot_vm() {
    # test VM done with test user, so can test non-admin
    openstack $as_doctor_user server list | grep -q " $VM_NAME " && return 0
    openstack $as_doctor_user server create --flavor "$VM_FLAVOR" \
                            --image "$IMAGE_NAME" \
                            "$VM_NAME"
    sleep 1
}

create_alarm() {
    # get vm_id as test user
    ceilometer $as_doctor_user alarm-list | grep -q " $ALARM_NAME " && return 0
    vm_id=$(openstack $as_doctor_user server list | grep " $VM_NAME " | awk '{print $2}')
    # TODO(r-mibu): change notification endpoint from localhost to the consumer
    # IP address (functest container).
    ceilometer $as_doctor_user alarm-event-create --name "$ALARM_NAME" \
        --alarm-action "http://localhost:$CONSUMER_PORT/failure" \
        --description "VM failure" \
        --enabled True \
        --repeat-actions False \
        --severity "moderate" \
        --event-type compute.instance.update \
        -q "traits.state=string::error; traits.instance_id=string::$vm_id"
}

start_monitor() {
    pgrep -f "python monitor.py" && return 0
    sudo -E python monitor.py "$COMPUTE_HOST" "$COMPUTE_IP" "$INSPECTOR_TYPE" \
        "http://127.0.0.1:$INSPECTOR_PORT/events" > monitor.log 2>&1 &
}

stop_monitor() {
    pgrep -f "python monitor.py" || return 0
    sudo kill $(pgrep -f "python monitor.py")
}

start_consumer() {
    pgrep -f "python consumer.py" && return 0
    python consumer.py "$CONSUMER_PORT" > consumer.log 2>&1 &

    # NOTE(r-mibu): create tunnel to the controller nodes, so that we can
    # avoid some network problems dpends on infra and installers.
    # This tunnel will be terminated by stop_consumer() or after 10 mins passed.
    if ! is_installer local; then
        for ip in $CONTROLLER_IPS
        do
            forward_rule="-R $CONSUMER_PORT:localhost:$CONSUMER_PORT"
            tunnel_command="sudo ssh $ssh_opts_cpu $COMPUTE_USER@$ip $forward_rule sleep 600"
            $tunnel_command > "ssh_tunnel.${ip}.log" 2>&1 < /dev/null &
        done
    fi
}

stop_consumer() {
    pgrep -f "python consumer.py" || return 0
    kill $(pgrep -f "python consumer.py")

    # NOTE(r-mibu): terminate tunnels to the controller nodes
    if ! is_installer local; then
        for ip in $CONTROLLER_IPS
        do
            forward_rule="-R $CONSUMER_PORT:localhost:$CONSUMER_PORT"
            tunnel_command="sudo ssh $ssh_opts_cpu $COMPUTE_USER@$ip $forward_rule sleep 600"
            kill $(pgrep -f "$tunnel_command")
        done
    fi
}

wait_for_vm_launch() {
    echo "waiting for vm launch..."

    count=0
    while [[ ${count} -lt 60 ]]
    do
        state=$(openstack $as_doctor_user server list | grep " $VM_NAME " | awk '{print $6}')
        if [[ "$state" == "ACTIVE" ]]; then
            # NOTE(cgoncalves): sleeping for a bit to stabilize
            # See python-openstackclient/functional/tests/compute/v2/test_server.py:wait_for_status
            sleep 5
            return 0
        fi
        if [[ "$state" == "ERROR" ]]; then
            openstack $as_doctor_user server show $VM_NAME
            die $LINENO "vm state is ERROR"
        fi
        count=$(($count+1))
        sleep 1
    done
    die $LINENO "Time out while waiting for VM launch"
}

inject_failure() {
    echo "disabling network of compute host [$COMPUTE_HOST] for 3 mins..."
    cat > disable_network.sh << 'END_TXT'
#!/bin/bash -x
dev=$(sudo ip a | awk '/ @COMPUTE_IP@\//{print $7}')
[[ -n "$dev" ]] || dev=$(sudo ip a | awk '/ @COMPUTE_IP@\//{print $5}')
sleep 1
sudo ip link set $dev down
echo "doctor set host down at" $(date "+%s.%N")
sleep 180
sudo ip link set $dev up
sleep 1
END_TXT
    sed -i -e "s/@COMPUTE_IP@/$COMPUTE_IP/" disable_network.sh
    chmod +x disable_network.sh
    scp $ssh_opts_cpu disable_network.sh "$COMPUTE_USER@$COMPUTE_IP:"
    ssh $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP" 'nohup ./disable_network.sh > disable_network.log 2>&1 &'
}

profile_performance_poc() {
    triggered=$(grep "^doctor set host down at" disable_network.log |\
                sed -e "s/^.* at //")
    vmdown=$(grep "doctor mark vm.* error at" inspector.log |tail -n 1 |\
               sed -e "s/^.* at //")
    hostdown=$(grep "doctor mark host.* down at" inspector.log |\
               sed -e "s/^.* at //")

    #calculate the relative interval to triggered(T00)
    export DOCTOR_PROFILER_T00=0
    export DOCTOR_PROFILER_T01=$(echo "($detected-$triggered)*1000/1" |bc)
    export DOCTOR_PROFILER_T03=$(echo "($vmdown-$triggered)*1000/1" |bc)
    export DOCTOR_PROFILER_T04=$(echo "($hostdown-$triggered)*1000/1" |bc)
    export DOCTOR_PROFILER_T09=$(echo "($notified-$triggered)*1000/1" |bc)

    python profiler-poc.py
}

calculate_notification_time() {
    if ! grep -q "doctor consumer notified at" consumer.log ; then
        die $LINENO "Consumer hasn't received fault notification."
    fi

    #keep 'at' as the last keyword just before the value, and
    #use regex to get value instead of the fixed column
    detected=$(grep "doctor monitor detected at" monitor.log |\
               sed -e "s/^.* at //")
    notified=$(grep "doctor consumer notified at" consumer.log |\
               sed -e "s/^.* at //")

    if [[ "$PROFILER_TYPE" == "poc" ]]; then
        profile_performance_poc
    fi

    echo "$notified $detected" | \
        awk '{
            d = $1 - $2;
            if (d < 1 && d > 0) { print d " OK"; exit 0 }
            else { print d " NG"; exit 1 }
        }'
}

check_host_status() {
    expected_state=$1

    host_status_line=$(openstack $as_doctor_user --os-compute-api-version 2.16 \
                       server show $VM_NAME | grep "host_status")
    host_status=$(echo $host_status_line | awk '{print $4}')
    die_if_not_set $LINENO host_status "host_status not reported by: nova show $VM_NAME"
    if [[ "$expected_state" =~ "$host_status" ]] ; then
        echo "$VM_NAME showing host_status: $host_status"
    else
        die $LINENO "host_status:$host_status not equal to expected_state: $expected_state"
    fi
}

unset_forced_down_hosts() {
    for host in $(openstack compute service list --service nova-compute \
                  -f value -c Host -c State | sed -n -e '/down$/s/ *down$//p')
    do
        # TODO (r-mibu): make sample inspector use keystone v3 api
        OS_AUTH_URL=${OS_AUTH_URL/v3/v2.0} \
        python ./nova_force_down.py $host --unset
    done

    echo "waiting disabled compute host back to be enabled..."
    wait_until 'openstack compute service list --service nova-compute
                -f value -c State | grep -q down' 240 5
}

cleanup() {
    set +e
    echo "cleanup..."
    stop_monitor
    stop_inspector
    stop_consumer

    unset_forced_down_hosts
    # TODO: We need to make sure the target compute host is back to IP
    #       reachable. wait_ping() will be added by tojuvone .
    sleep 110
    if is_set COMPUTE_IP; then
        scp $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP:disable_network.log" .
    fi

    openstack $as_doctor_user server list | grep -q " $VM_NAME " && openstack $as_doctor_user server delete "$VM_NAME"
    sleep 1
    alarm_id=$(ceilometer $as_doctor_user alarm-list | grep " $ALARM_NAME " | awk '{print $2}')
    sleep 1
    [ -n "$alarm_id" ] && ceilometer $as_doctor_user alarm-delete "$alarm_id"
    sleep 1

    image_id=$(openstack image list | grep " $IMAGE_NAME " | awk '{print $2}')
    sleep 1
    #if an existing image was used, there's no need to remove it here
    if [[ "$use_existing_image" == false ]] ; then
        [ -n "$image_id" ] && openstack image delete "$image_id"
    fi
    openstack role remove "$DOCTOR_ROLE" --user "$DOCTOR_USER" \
                              --project "$DOCTOR_PROJECT"
    openstack project delete "$DOCTOR_PROJECT"
    openstack user delete "$DOCTOR_USER"

    cleanup_installer
    cleanup_inspector
}

# Main process

echo "Note: doctor/tests/run.sh has been executed."
git log --oneline -1 || true   # ignore even you don't have git installed

trap cleanup EXIT

source $TOP_DIR/functions-common
source $TOP_DIR/lib/installer
source $TOP_DIR/lib/inspector

setup_installer

echo "preparing VM image..."
download_image
register_image

echo "creating test user..."
create_test_user

echo "creating VM..."
boot_vm
wait_for_vm_launch

echo "get computer host info..."
get_compute_host_info

echo "creating alarm..."
#TODO: change back to use, network problems depends on infra and installers
#get_consumer_ip
create_alarm

echo "starting doctor sample components..."
start_inspector
start_monitor
start_consumer

sleep 60
echo "injecting host failure..."
inject_failure
sleep 60

check_host_status "(DOWN|UNKNOWN)"
calculate_notification_time

echo "done"
