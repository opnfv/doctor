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
VM_BASENAME=doctor_vm
VM_FLAVOR=m1.tiny
#if VM_COUNT set, use that instead
VM_COUNT=${VM_COUNT:-1}
NET_NAME=doctor_net
NET_CIDR=192.168.168.0/24
ALARM_BASENAME=doctor_alarm
CONSUMER_PORT=12346
DOCTOR_USER=doctor
DOCTOR_PW=doctor
DOCTOR_PROJECT=doctor
DOCTOR_ROLE=_member_
PROFILER_TYPE=${PROFILER_TYPE:-poc}
PYTHON_ENABLE=${PYTHON_ENABLE:-false}

TOP_DIR=$(cd $(dirname "$0") && pwd)

as_doctor_user="--os-username $DOCTOR_USER --os-password $DOCTOR_PW
                --os-project-name $DOCTOR_PROJECT --os-tenant-name $DOCTOR_PROJECT"
# NOTE: ceilometer command still requires '--os-tenant-name'.
#ceilometer="ceilometer ${as_doctor_user/--os-project-name/--os-tenant-name}"
ceilometer="ceilometer $as_doctor_user"
as_admin_user="--os-username admin --os-project-name $DOCTOR_PROJECT
               --os-tenant-name $DOCTOR_PROJECT"


# Functions

get_compute_host_info() {
    # get computer host info which first VM boot in as admin user
    COMPUTE_HOST=$(openstack $as_admin_user server show ${VM_BASENAME}1 |
                   grep "OS-EXT-SRV-ATTR:host " | awk '{ print $4 }')
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
        openstack project create --description "Doctor Project" \
                                 "$DOCTOR_PROJECT"
    }
    openstack user list | grep -q " $DOCTOR_USER " || {
        openstack user create "$DOCTOR_USER" --password "$DOCTOR_PW" \
                              --project "$DOCTOR_PROJECT"
    }
    openstack role show "$DOCTOR_ROLE" | grep -q " $DOCTOR_ROLE " || {
        openstack role create "$DOCTOR_ROLE"
    }
    openstack role assignment list --user "$DOCTOR_USER" \
    --project "$DOCTOR_PROJECT" --names | grep -q " $DOCTOR_ROLE " || {
        openstack role add "$DOCTOR_ROLE" --user "$DOCTOR_USER" \
                           --project "$DOCTOR_PROJECT"
    }
    openstack role assignment list --user admin --project "$DOCTOR_PROJECT" \
    --names | grep -q " admin " || {
        openstack role add admin --user admin --project "$DOCTOR_PROJECT"
    }
    # tojuvone: openstack quota show is broken and have to use nova
    # https://bugs.launchpad.net/manila/+bug/1652118
    # Note! while it is encouraged to use openstack client it has proven
    # quite buggy.
    # QUOTA=$(openstack quota show $DOCTOR_PROJECT)
    DOCTOR_QUOTA=$(nova quota-show --tenant $DOCTOR_PROJECT)
    # We make sure that quota allows number of instances and cores
    OLD_INSTANCE_QUOTA=$(echo "${DOCTOR_QUOTA}" | grep " instances " | \
                         awk '{print $4}')
    if [ $OLD_INSTANCE_QUOTA -lt $VM_COUNT ]; then
        openstack quota set --instances $VM_COUNT \
                  $DOCTOR_USER
    fi
    OLD_CORES_QUOTA=$(echo "${DOCTOR_QUOTA}" | grep " cores " | \
                      awk '{print $4}')
    if [ $OLD_CORES_QUOTA -lt $VM_COUNT ]; then
        openstack quota set --cores $VM_COUNT \
                  $DOCTOR_USER
    fi
}

remove_test_user() {
    openstack project list | grep -q " $DOCTOR_PROJECT " && {
        openstack role assignment list --user admin \
        --project "$DOCTOR_PROJECT" --names | grep -q " admin " && {
            openstack role remove admin --user admin --project "$DOCTOR_PROJECT"
        }
        openstack user list | grep -q " $DOCTOR_USER " && {
            openstack role assignment list --user "$DOCTOR_USER" \
            --project "$DOCTOR_PROJECT" --names | grep -q " $DOCTOR_ROLE " && {
                openstack role remove "$DOCTOR_ROLE" --user "$DOCTOR_USER" \
                --project "$DOCTOR_PROJECT"
            }
            openstack user delete "$DOCTOR_USER"
        }
        openstack project delete "$DOCTOR_PROJECT"
    }
}

boot_vm() {
    # test VM done with test user, so can test non-admin

    if ! openstack $as_doctor_user network show $NET_NAME; then
        openstack $as_doctor_user network create $NET_NAME
    fi
    if ! openstack $as_doctor_user subnet show $NET_NAME; then
        openstack $as_doctor_user subnet create $NET_NAME \
            --network $NET_NAME --subnet-range $NET_CIDR --no-dhcp
    fi
    net_id=$(openstack $as_doctor_user network show $NET_NAME -f value -c id)

    servers=$(openstack $as_doctor_user server list)
    for i in `seq $VM_COUNT`; do
        echo "${servers}" | grep -q " $VM_BASENAME$i " && continue
        openstack $as_doctor_user server create --flavor "$VM_FLAVOR" \
            --image "$IMAGE_NAME" --nic net-id=$net_id "$VM_BASENAME$i"
    done
    sleep 1
}

create_alarm() {
    # get vm_id as test user
    alarm_list=$($ceilometer alarm-list)
    vms=$(openstack $as_doctor_user server list)
    for i in `seq $VM_COUNT`; do
        echo "${alarm_list}" | grep -q " $ALARM_BASENAME$i " || {
            vm_id=$(echo "${vms}" | grep " $VM_BASENAME$i " | awk '{print $2}')
            # TODO(r-mibu): change notification endpoint from localhost to the
            # consumer. IP address (functest container).
            $ceilometer alarm-event-create \
                       --name "$ALARM_BASENAME$i" \
                       --alarm-action "http://localhost:$CONSUMER_PORT/failure" \
                       --description "VM failure" \
                       --enabled True \
                       --repeat-actions False \
                       --severity "moderate" \
                       --event-type compute.instance.update \
                       -q "traits.state=string::error; \
                       traits.instance_id=string::$vm_id"
            }
     done
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
        active_count=0
        vms=$(openstack $as_doctor_user server list)
        for i in `seq $VM_COUNT`; do
            state=$(echo "${vms}" | grep " $VM_BASENAME$i " | awk '{print $6}')
            if [[ "$state" == "ACTIVE" ]]; then
                active_count=$(($active_count+1))
            elif [[ "$state" == "ERROR" ]]; then
                die $LINENO "vm state $VM_BASENAME$i is ERROR"
            else
                #This VM not yet active
                count=$(($count+1))
                sleep 5
                continue
            fi
        done
        [[ $active_count -eq $VM_COUNT ]] && {
            echo "get computer host info..."
            get_compute_host_info
            VMS_ON_FAILED_HOST=$(openstack $as_doctor_user server list --host \
                         $COMPUTE_HOST | grep " ${VM_BASENAME}" |  wc -l)
            return 0
        }
        #Not all VMs active
        count=$(($count+1))
        sleep 5
    done
    die $LINENO "Time out while waiting for VM launch"
}

inject_failure() {
    echo "disabling network of compute host [$COMPUTE_HOST] for 3 mins..."
    cat > disable_network.sh << 'END_TXT'
#!/bin/bash -x
sleep 1
if [ -n "@INTERFACE_NAME@" ]; then
    dev=@INTERFACE_NAME@
else
    dev=$(sudo ip a | awk '/ @COMPUTE_IP@\//{print $NF}')
fi
sudo ip link set $dev down
echo "doctor set link down at" $(date "+%s.%N")
sleep 180
sudo ip link set $dev up
sleep 1
END_TXT
    sed -i -e "s/@COMPUTE_IP@/$COMPUTE_IP/" disable_network.sh
    sed -i -e "s/@INTERFACE_NAME@/$INTERFACE_NAME/" disable_network.sh
    chmod +x disable_network.sh
    scp $ssh_opts_cpu disable_network.sh "$COMPUTE_USER@$COMPUTE_IP:"
    ssh $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP" 'nohup ./disable_network.sh > disable_network.log 2>&1 &'
    # use host time to get rid of potential time sync deviation between nodes
    triggered=$(date "+%s.%N")
}

wait_consumer() {
    local interval=1
    local rounds=$(($1 / $interval))
    for i in `seq $rounds`; do
        notified_count=$(grep "doctor consumer notified at" consumer.log | wc -l)
        if [[ $notified_count -eq  $VMS_ON_FAILED_HOST ]]; then
            return 0
        fi
        sleep $interval
    done
    die $LINENO "Consumer hasn't received fault notification."
}

calculate_notification_time() {
    wait_consumer 60
    #keep 'at' as the last keyword just before the value, and
    #use regex to get value instead of the fixed column
    if [ ! -f monitor.log ]; then
        scp $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP:monitor.log" .
    fi
    detected=$(grep "doctor monitor detected at" monitor.log |\
               sed -e "s/^.* at //" | tail -1)
    notified=$(grep "doctor consumer notified at" consumer.log |\
               sed -e "s/^.* at //" | tail -1)

    echo "$notified $detected" | \
        awk '{
            d = $1 - $2;
            if (d < 1 && d > 0) { print d " OK"; exit 0 }
            else { print d " NG"; exit 1 }
        }'
}

check_host_status() {
    # Check host related to first Doctor VM is in wanted state
    # $1    Expected state
    # $2    Seconds to wait to have wanted state
    expected_state=$1
    local interval=5
    local rounds=$(($2 / $interval))
    for i in `seq $rounds`; do
        host_status_line=$(openstack $as_doctor_user --os-compute-api-version \
                           2.16 server show ${VM_BASENAME}1 | grep "host_status")
        host_status=$(echo $host_status_line | awk '{print $4}')
        die_if_not_set $LINENO host_status "host_status not reported by: nova show ${VM_BASENAME}1"
        if [[ "$expected_state" =~ "$host_status" ]] ; then
            echo "${VM_BASENAME}1 showing host_status: $host_status"
            return 0
        else
            sleep $interval
        fi
    done
    if [[ "$expected_state" =~ "$host_status" ]] ; then
        echo "${VM_BASENAME}1 showing host_status: $host_status"
    else
        die $LINENO  "host_status:$host_status not equal to expected_state: $expected_state"
    fi
}

unset_forced_down_hosts() {
    # for debug
    openstack compute service list --service nova-compute

    downed_computes=$(openstack compute service list --service nova-compute \
                      -f value -c Host -c State | grep ' down$' \
                      | sed -e 's/ *down$//')
    echo "downed_computes: $downed_computes"
    for host in $downed_computes
    do
        # TODO(r-mibu): use openstack client
        #openstack compute service set --up $host nova-compute
        nova service-force-down --unset $host nova-compute
    done

    echo "waiting disabled compute host back to be enabled..."
    wait_until 'openstack compute service list --service nova-compute
                -f value -c State | grep -q down' 240 5

    for host in $downed_computes
    do
        # TODO(r-mibu): improve 'get_compute_ip_from_hostname'
        get_compute_ip_from_hostname $host
        wait_until "! ping -c 1 $COMPUTE_IP" 120 5
    done
}

collect_logs() {
    if [[ -n "$COMPUTE_IP" ]];then
        scp $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP:disable_network.log" .
    fi

    # TODO(yujunz) collect other logs, e.g. nova, aodh
}

run_profiler() {
    if [[ "$PROFILER_TYPE" == "poc" ]]; then
        linkdown=$(grep "doctor set link down at " disable_network.log |\
                  sed -e "s/^.* at //")
        vmdown=$(grep "doctor mark vm.* error at" inspector.log |tail -n 1 |\
                 sed -e "s/^.* at //")
        hostdown=$(grep "doctor mark host.* down at" inspector.log |\
                 sed -e "s/^.* at //")

        # TODO(yujunz) check the actual delay to verify time sync status
        # expected ~1s delay from $trigger to $linkdown
        relative_start=${linkdown}
        export DOCTOR_PROFILER_T00=$(python -c \
          "print(int(($linkdown-$relative_start)*1000))")
        export DOCTOR_PROFILER_T01=$(python -c \
          "print(int(($detected-$relative_start)*1000))")
        export DOCTOR_PROFILER_T03=$(python -c \
          "print(int(($vmdown-$relative_start)*1000))")
        export DOCTOR_PROFILER_T04=$(python -c \
          "print(int(($hostdown-$relative_start)*1000))")
        export DOCTOR_PROFILER_T09=$(python -c \
          "print(int(($notified-$relative_start)*1000))")

        python profiler-poc.py > doctor_profiler.log 2>&1
    fi
}

cleanup() {
    set +e
    echo "cleanup..."
    stop_inspector
    stop_consumer

    unset_forced_down_hosts
    stop_monitor
    collect_logs

    vms=$(openstack $as_doctor_user server list)
    vmstodel=""
    for i in `seq $VM_COUNT`; do
        $(echo "${vms}" | grep -q " $VM_BASENAME$i ") &&
        vmstodel+=" $VM_BASENAME$i"
    done
    [[ $vmstodel ]] && openstack $as_doctor_user server delete $vmstodel
    alarm_list=$($ceilometer alarm-list)
    for i in `seq $VM_COUNT`; do
        alarm_id=$(echo "${alarm_list}" | grep " $ALARM_BASENAME$i " |
                   awk '{print $2}')
        [ -n "$alarm_id" ] && $ceilometer alarm-delete "$alarm_id"
    done
    openstack $as_doctor_user subnet delete $NET_NAME
    sleep 1
    openstack $as_doctor_user network delete $NET_NAME
    sleep 1

    image_id=$(openstack image list | grep " $IMAGE_NAME " | awk '{print $2}')
    sleep 1
    #if an existing image was used, there's no need to remove it here
    if [[ "$use_existing_image" == false ]] ; then
        [ -n "$image_id" ] && openstack image delete "$image_id"
    fi

    remove_test_user

    cleanup_installer
    cleanup_inspector
    cleanup_monitor

    # NOTE: Temporal log printer.
    for f in $(find . -name '*.log')
    do
        echo
        echo "[$f]"
        sed -e 's/^/ | /' $f
        echo
    done
}

setup_python_packages() {
    sudo pip install flask==0.10.1
    command -v openstack || sudo pip install python-openstackclient==2.3.0
    command -v ceilometer || sudo pip install python-ceilometerclient==2.6.2
    command -v congress || sudo pip install python-congressclient==1.5.0
}

# Main process

if [[ $PYTHON_ENABLE == [Tt]rue ]]; then
    which tox || sudo pip install tox
    if [ -f /usr/bin/apt-get ]; then
        sudo apt-get install -y python3-dev
    elif [ -f /usr/bin/yum ] ; then
        sudo yum install -y python3-devel
    fi

    cd $TOP_DIR
    echo "executing tox..."
    tox
    exit $?
fi

echo "Note: doctor/tests/run.sh has been executed."
git log --oneline -1 || true   # ignore even you don't have git installed

trap cleanup EXIT

setup_python_packages

source $TOP_DIR/functions-common
source $TOP_DIR/lib/installer
source $TOP_DIR/lib/inspector
source $TOP_DIR/lib/monitor

rm -f *.log

setup_installer

echo "preparing VM image..."
download_image
register_image

echo "creating test user..."
create_test_user

echo "creating VM..."
boot_vm
wait_for_vm_launch

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

check_host_status "(DOWN|UNKNOWN)" 60
unset_forced_down_hosts
calculate_notification_time
collect_logs
run_profiler

echo "done"
