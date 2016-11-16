#!/bin/bash -e
##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

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

SUPPORTED_INSPECTOR_TYPES="sample congress"
INSPECTOR_TYPE=${INSPECTOR_TYPE:-sample}
TOP_DIR=$(cd $(dirname "$0") && pwd)

ssh_opts="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
as_doctor_user="--os-username $DOCTOR_USER --os-password $DOCTOR_PW
                --os-tenant-name $DOCTOR_PROJECT"

if [[ ! "$SUPPORTED_INSPECTOR_TYPES" =~ "$INSPECTOR_TYPE" ]] ; then
    echo "ERROR: INSPECTOR_TYPE=$INSPECTOR_TYPE is not supported."
    exit 1
fi

get_compute_host_info() {
    # get computer host info which VM boot in
    COMPUTE_HOST=$(openstack $as_doctor_user server show $VM_NAME |
                   grep "OS-EXT-SRV-ATTR:host" | awk '{ print $4 }')
    compute_host_in_undercloud=${COMPUTE_HOST%%.*}
    die_if_not_set $LINENO COMPUTE_HOST "Failed to get compute hostname"

    if is_installer apex; then
        COMPUTE_USER=${COMPUTE_USER:-heat-admin}
        COMPUTE_IP=$(sudo ssh $ssh_opts $INSTALLER_IP \
             "source stackrc; \
             nova show $compute_host_in_undercloud \
             | awk '/ ctlplane network /{print \$5}'")
    elif is_installer fuel; then
        COMPUTE_USER=${COMPUTE_USER:-root}
        node_id=$(echo $compute_host_in_undercloud | cut -d "-" -f 2)
        COMPUTE_IP=$(sshpass -p r00tme ssh 2>/dev/null $ssh_opts root@${INSTALLER_IP} \
             "fuel node|awk -F '|' -v id=$node_id '{if (\$1 == id) print \$5}' |xargs")
    elif is_installer local; then
        COMPUTE_USER=${COMPUTE_USER:-$(whoami)}
        COMPUTE_IP=$(getent hosts "$COMPUTE_HOST" | awk '{ print $1 }')
    fi

    die_if_not_set $LINENO COMPUTE_IP "Could not resolve $COMPUTE_HOST. Either manually set COMPUTE_IP or enable DNS resolution."
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

get_consumer_ip() {
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

print_log() {
    log_file=$1
    echo "$log_file:"
    sed -e 's/^/    /' "$log_file"
}

start_monitor() {
    pgrep -f "python monitor.py" && return 0
    sudo -E python monitor.py "$COMPUTE_HOST" "$COMPUTE_IP" "$INSPECTOR_TYPE" \
        "http://127.0.0.1:$INSPECTOR_PORT/events" > monitor.log 2>&1 &
}

stop_monitor() {
    pgrep -f "python monitor.py" || return 0
    sudo kill $(pgrep -f "python monitor.py")
    print_log monitor.log
}

congress_add_rule() {
    name=$1
    policy=$2
    rule=$3

    if ! openstack congress policy rule list $policy | grep -q -e "// Name: $name$" ; then
        openstack congress policy rule create --name $name $policy "$rule"
    fi
}

congress_del_rule() {
    name=$1
    policy=$2

    if openstack congress policy rule list $policy | grep -q -e "^// Name: $name$" ; then
        openstack congress policy rule delete $policy $name
    fi
}

congress_setup_rules() {
    congress_add_rule host_down classification \
        'host_down(host) :-
            doctor:events(hostname=host, type="compute.host.down", status="down")'

    congress_add_rule active_instance_in_host classification \
        'active_instance_in_host(vmid, host) :-
            nova:servers(id=vmid, host_name=host, status="ACTIVE")'

    congress_add_rule host_force_down classification \
        'execute[nova:services.force_down(host, "nova-compute", "True")] :-
            host_down(host)'

    congress_add_rule error_vm_states classification \
        'execute[nova:servers.reset_state(vmid, "error")] :-
            host_down(host),
            active_instance_in_host(vmid, host)'
}

start_inspector() {
    if [[ "$INSPECTOR_TYPE" == "sample" ]] ; then
        pgrep -f "python inspector.py" && return 0
        python inspector.py "$INSPECTOR_PORT" > inspector.log 2>&1 &
    elif [[ "$INSPECTOR_TYPE" == "congress" ]] ; then
        nova_api_min_version="2.11"
        nova_api_version=$(openstack congress datasource list | \
                           grep nova | grep -Po "(?<='api_version': ')[^']*")
        if ! is_set nova_api_version; then
            nova_api_version="2.0"
        fi
        if [[ "$nova_api_version" < "$nova_api_min_version" ]]; then
            die $LINENO "Congress Nova datasource API version < $nova_api_min_version ($nova_api_version)"
        fi
        openstack congress driver list | grep -q " doctor "
        openstack congress datasource list | grep -q " doctor " || {
            openstack congress datasource create doctor doctor
        }
        congress_setup_rules
    fi
}

stop_inspector() {
    if [[ "$INSPECTOR_TYPE" == "sample" ]] ; then
        pgrep -f "python inspector.py" || return 0
        kill $(pgrep -f "python inspector.py")
        print_log inspector.log
    elif [[ "$INSPECTOR_TYPE" == "congress" ]] ; then
        congress_del_rule host_force_down classification
        congress_del_rule error_vm_states classification
        congress_del_rule active_instance_in_host classification
        congress_del_rule host_down classification
    fi
}

start_consumer() {
    pgrep -f "python consumer.py" && return 0
    python consumer.py "$CONSUMER_PORT" > consumer.log 2>&1 &

    # NOTE(r-mibu): create tunnel to the controller nodes, so that we can
    # avoid some network problems dpends on infra and installers.
    # This tunnel will be terminated by stop_consumer() or after 10 mins passed.
    if ! is_installer local; then
        if is_installer apex; then
            CONTROLLER_IPS=$(sudo ssh $ssh_opts $INSTALLER_IP \
                             "source stackrc; \
                             nova list | grep ' overcloud-controller-[0-9] ' \
                             | sed -e 's/^.*ctlplane=//' -e 's/ *|\$//'")
        elif is_installer fuel; then
            CONTROLLER_IPS=$(sshpass -p r00tme ssh 2>/dev/null $ssh_opts root@${INSTALLER_IP} \
                            "fuel node | grep controller | cut -d '|' -f 5|xargs")
        fi

        die_if_not_set $LINENO CONTROLLER_IPS "Could not get CONTROLLER_IPS."
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
    print_log consumer.log

    # NOTE(r-mibu): terminate tunnels to the controller nodes
    if ! is_installer local; then
        for ip in $CONTROLLER_IPS
        do
            forward_rule="-R $CONSUMER_PORT:localhost:$CONSUMER_PORT"
            tunnel_command="sudo ssh $ssh_opts_cpu $COMPUTE_USER@$ip $forward_rule sleep 600"
            kill $(pgrep -f "$tunnel_command")
            print_log "ssh_tunnel.${ip}.log"
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
sleep 1
sudo ip link set $dev down
sleep 180
sudo ip link set $dev up
sleep 1
END_TXT
    sed -i -e "s/@COMPUTE_IP@/$COMPUTE_IP/" disable_network.sh
    chmod +x disable_network.sh
    scp $ssh_opts_cpu disable_network.sh "$COMPUTE_USER@$COMPUTE_IP:"
    ssh $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP" 'nohup ./disable_network.sh > disable_network.log 2>&1 &'
}

calculate_notification_time() {
    detected=$(grep "doctor monitor detected at" monitor.log | awk '{print $10}')
    notified=$(grep "doctor consumer notified at" consumer.log | awk '{print $10}')
    if ! grep -q "doctor consumer notified at" consumer.log ; then
        die $LINENO "Consumer hasn't received fault notification."
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

cleanup() {
    set +e
    echo "cleanup..."
    stop_monitor
    stop_inspector
    stop_consumer

    echo "waiting disabled compute host back to be enabled..."
    python ./nova_force_down.py "$COMPUTE_HOST" --unset
    sleep 240
    check_host_status "UP"
    scp $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP:disable_network.log" .
    print_log disable_network.log

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
}


echo "Note: doctor/tests/run.sh has been executed."

trap cleanup EXIT

source $TOP_DIR/functions-common
source $TOP_DIR/lib/installer

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
