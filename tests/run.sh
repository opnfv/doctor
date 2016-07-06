#!/bin/bash -e
##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

[[ "${CI_DEBUG:-true}" == "true" ]] && set -x

IMAGE_URL=https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
IMAGE_NAME=cirros
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

SUPPORTED_INSTALLER_TYPES="apex local"
INSTALLER_TYPE=${INSTALLER_TYPE:-apex}
INSTALLER_IP=${INSTALLER_IP:-none}
COMPUTE_HOST=none
COMPUTE_IP=none
COMPUTE_USER=none
ssh_opts="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

if [[ ! "$SUPPORTED_INSTALLER_TYPES" =~ "$INSTALLER_TYPE" ]] ; then
    echo "ERROR: INSTALLER_TYPE=$INSTALLER_TYPE is not supported."
    exit 1
fi

get_install_info() {
    if [[ "$INSTALLER_TYPE" == "apex" ]] ; then
        if [[ "$INSTALLER_IP" == "none" ]] ; then
            instack_mac=$(sudo virsh domiflist instack | awk '/default/{print $5}')
            INSTALLER_IP=$(/usr/sbin/arp -e | grep ${instack_mac} | awk '{print $1}')
        fi
    fi
}

get_compute_host_info() {
    if [[ "$INSTALLER_TYPE" == "apex" ]] ; then
        COMPUTE_USER="heat-admin"
        (
            change_to_doctor_user

            # get computer host info which VM boot in
            export COMPUTE_HOST=$(openstack server show $VM_NAME | \
                    grep "OS-EXT-SRV-ATTR:host") | awk '{ print $4 }' |
                    awk -F '.' '{print $1}')
        )
        # get compute ip from install ?
        COMPUTE_IP=?
    elif [[ "$INSTALLER_TYPE" == "local" ]] ; then
        COMPUTE_USER=$(whoami)
        COMPUTE_HOST=`hostname`
        COMPUTE_IP=$(getent hosts "$COMPUTE_HOST" | awk '{ print $1 }')
        if [[ -z "$COMPUTE_IP" ]]; then
            echo "ERROR: Could not resolve $COMPUTE_HOST. Either manually set COMPUTE_IP or enable DNS resolution."
            exit 1
        fi
    fi

    # verify connectivity to target compute host
    ping -c 1 "$COMPUTE_IP"
	if [[ $? -ne 0 ]] ; then
	    echo "ERROR: can not ping to computer host"
	    exit 1
	fi
}

prepare_compute_ssh() {
    ssh_opts_cpu="$ssh_opts"

    # get ssh key from installer node
    if [[ "$INSTALLER_TYPE" == "apex" ]] ; then
        sudo scp $ssh_opts root@"$INSTALLER_IP":/home/stack/.ssh/id_rsa instack_key
    elif [[ "$INSTALLER_TYPE" == "local" ]] ; then
        echo "INSTALLER_TYPE set to 'local'. Assuming SSH keys already exchanged with $COMPUTE_HOST"
    fi

    sudo chown $(whoami):$(whoami) instack_key
    chmod 400 instack_key
    ssh_opts_cpu+=" -i instack_key"

    # verify ssh to target compute host
    ssh $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP" 'exit'
    if [[ $? -ne 0 ]] ; then
	    echo "ERROR: can not ssh to computer host"
	    exit 1
	fi
}

download_image() {
    [ -e "$IMAGE_FILE" ] && return 0
    wget "$IMAGE_URL" -o "$IMAGE_FILE"
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
    openstack user list | grep -q " $DOCTOR_USER " || {
        openstack user create "$DOCTOR_USER" --password "$DOCTOR_PW"
    }
    openstack project list | grep -q " $DOCTOR_PROJECT " || {
        openstack project create "$DOCTOR_PROJECT"
    }
    openstack user role list "$DOCTOR_USER" --project "$DOCTOR_PROJECT" \
    | grep -q " $DOCTOR_ROLE " || {
        openstack role add "$DOCTOR_ROLE" --user "$DOCTOR_USER" \
                           --project "$DOCTOR_PROJECT"
    }
}

change_to_doctor_user() {
    export OS_USERNAME="$DOCTOR_USER"
    export OS_PASSWORD="$DOCTOR_PW"
    export OS_PROJECT_NAME="$DOCTOR_PROJECT"
    export OS_TENANT_NAME="$DOCTOR_PROJECT"
}

boot_vm() {
    (
        # test VM done with test user, so can test non-admin
        change_to_doctor_user
        openstack server list | grep -q " $VM_NAME " && return 0
        openstack server create --flavor "$VM_FLAVOR" \
                                --image "$IMAGE_NAME" \
                                "$VM_NAME"
        sleep 1
    )

}

create_alarm() {
    (
        # get vm_id as test user
        change_to_doctor_user
        ceilometer alarm-list | grep -q " $ALARM_NAME " && return 0
        vm_id=$(openstack server list | grep " $VM_NAME " | awk '{print $2}')
        ceilometer alarm-event-create --name "$ALARM_NAME" \
            --alarm-action "http://localhost:$CONSUMER_PORT/failure" \
            --description "VM failure" \
            --enabled True \
            --repeat-actions False \
            --severity "moderate" \
            --event-type compute.instance.update \
            -q "traits.state=string::error; traits.instance_id=string::$vm_id"
    )
}


start_monitor() {
    pgrep -f "python monitor.py" && return 0
    sudo python monitor.py "$COMPUTE_HOST" "$COMPUTE_IP" \
        "http://127.0.0.1:$INSPECTOR_PORT/events" > monitor.log 2>&1 &
}

stop_monitor() {
    pgrep -f "python monitor.py" || return 0
    sudo kill $(pgrep -f "python monitor.py")
    cat monitor.log
}

start_inspector() {
    pgrep -f "python inspector.py" && return 0
    python inspector.py "$INSPECTOR_PORT" > inspector.log 2>&1 &
}

stop_inspector() {
    pgrep -f "python inspector.py" || return 0
    kill $(pgrep -f "python inspector.py")
    cat inspector.log
}

start_consumer() {
    pgrep -f "python consumer.py" && return 0
    python consumer.py "$CONSUMER_PORT" > consumer.log 2>&1 &
}

stop_consumer() {
    pgrep -f "python consumer.py" || return 0
    kill $(pgrep -f "python consumer.py")
    cat consumer.log
}

wait_for_vm_launch() {
    echo "waiting for vm launch..."

    (
        # get VM state as test user
        change_to_doctor_user

        count=0
        while [[ ${count} -lt 60 ]]
        do
            state=$(openstack server list | grep " $VM_NAME " | awk '{print $6}')
            [[ "$state" == "ACTIVE" ]] && return 0
            [[ "$state" == "ERROR" ]] && echo "vm state is ERROR" && exit 1
            count=$(($count+1))
            sleep 1
        done
        echo "ERROR: time out while waiting for vm launch"
        exit 1
    )
}

inject_failure() {
    echo "disabling network of compute host [$COMPUTE_HOST] for 3 mins..."
    cat > disable_network.sh << 'END_TXT'
#!/bin/bash -x
dev=$(sudo ip route | awk '/^default/{print $5}')
sleep 1
sudo ip link set $dev down
sleep 180
sudo ip link set $dev up
sleep 1
END_TXT
    chmod +x disable_network.sh
    scp $ssh_opts_cpu disable_network.sh "$COMPUTE_USER@$COMPUTE_IP:"
    ssh $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP" 'nohup ./disable_network.sh > disable_network.log 2>&1 &'
}

calculate_notification_time() {
    detected=$(grep "doctor monitor detected at" monitor.log | awk '{print $5}')
    notified=$(grep "doctor consumer notified at" consumer.log | awk '{print $5}')
    echo "$notified $detected" | \
        awk '{d = $1 - $2; if (d < 1 && d > 0) print d " OK"; else print d " NG"}'
}

check_host_status() {
    expect_state=$1
    (
        change_to_doctor_user

        host_status_line=$(openstack server show $VM_NAME | grep "host_status")
        if [[ $? -ne 0 ]] ; then
            echo "ERROR: host_status not configured for owner in Nova policy.json"
            exit 1
        fi

        host_status=$(echo $host_status_line | awk '{print $4}')
        if [ -z "$host_status" ] ; then
            echo "ERROR: host_status not reported by: nova show $VM_NAME"
            exit 1
        elif [[ "$host_status" != "$expect_state" ]] ; then
            echo "ERROR: host_status:$host_status not equal to expect_state: $expect_state"
            exit 1
        else
            echo "$VM_NAME showing host_status: $host_status"
        fi
    )
}

cleanup() {
    set +e
    echo "cleanup..."
    stop_monitor
    stop_inspector
    stop_consumer

    python ./nova_force_down.py "$COMPUTE_HOST" --unset
    sleep 1
    (
        change_to_doctor_user
        openstack server list | grep -q " $VM_NAME " && openstack server delete "$VM_NAME"
        sleep 1
        alarm_id=$(ceilometer alarm-list | grep " $ALARM_NAME " | awk '{print $2}')
        sleep 1
        [ -n "$alarm_id" ] && ceilometer alarm-delete "$alarm_id"
        sleep 1
    )
    image_id=$(openstack image list | grep " $IMAGE_NAME " | awk '{print $2}')
    sleep 1
    [ -n "$image_id" ] && openstack image delete "$image_id"
    openstack role remove "$DOCTOR_ROLE" --user "$DOCTOR_USER" \
                              --project "$DOCTOR_PROJECT"
    openstack project delete "$DOCTOR_PROJECT"
    openstack user delete "$DOCTOR_USER"

    echo "waiting disabled compute host back to be enabled..."
    sleep 180
    check_host_status "UP"
    ssh $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP" \
        "[ -e disable_network.log ] && cat disable_network.log"
}


echo "Note: doctor/tests/run.sh has been executed."

trap cleanup EXIT

echo "get installer info..."
get_install_info

echo "preparing VM image..."
download_image
register_image

echo "creating test user..."
create_test_user

echo "creating VM and alarm..."
boot_vm
wait_for_vm_launch
create_alarm

echo "get computer host info and prepare to ssh..."
get_compute_host_info
prepare_compute_ssh

echo "starting doctor sample components..."
start_monitor
start_inspector
start_consumer

sleep 60
echo "injecting host failure..."
inject_failure
sleep 10

check_host_status "DOWN"
calculate_notification_time

echo "done"
