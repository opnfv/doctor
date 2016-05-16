#!/bin/bash -ex
##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

IMAGE_URL=https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
IMAGE_NAME=cirros
IMAGE_FILE="${IMAGE_NAME}.img"
IMAGE_FORMAT=qcow2
VM_NAME=doctor_vm1
VM_FLAVOR=m1.tiny
ALARM_NAME=doctor_alarm1
INSPECTOR_PORT=12345
CONSUMER_PORT=12346
TEST_USER=demo
TEST_PW=demo
TEST_TENANT=demo

SUPPORTED_INSTALLER_TYPES="apex local"
INSTALLER_TYPE=${INSTALLER_TYPE:-apex}
INSTALLER_IP=${INSTALLER_IP:-none}
COMPUTE_HOST=${COMPUTE_HOST:-overcloud-novacompute-0}
COMPUTE_IP=${COMPUTE_IP:-none}
COMPUTE_USER=${COMPUTE_USER:-heat-admin}
ssh_opts="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

if [[ ! "$SUPPORTED_INSTALLER_TYPES" =~ "$INSTALLER_TYPE" ]] ; then
    echo "ERROR: INSTALLER_TYPE=$INSTALLER_TYPE is not supported."
    exit 1
fi

prepare_compute_ssh() {
    ssh_opts_cpu="$ssh_opts"

    if [[ "$INSTALLER_TYPE" == "apex" ]] ; then
        if [[ "$INSTALLER_IP" == "none" ]] ; then
            instack_mac=$(sudo virsh domiflist instack | awk '/default/{print $5}')
            INSTALLER_IP=$(/usr/sbin/arp -e | grep ${instack_mac} | awk '{print $1}')
        fi

        if [[ "$COMPUTE_IP" == "none" ]] ; then
            COMPUTE_IP=$(sudo ssh $ssh_opts $INSTALLER_IP \
                         "source stackrc; \
                          nova show $COMPUTE_HOST \
                          | awk '/ ctlplane network /{print \$5}'")
        fi

        # get ssh key from installer node
        sudo scp $ssh_opts root@"$INSTALLER_IP":/home/stack/.ssh/id_rsa instack_key
        sudo chown $(whoami):$(whoami) instack_key
        chmod 400 instack_key
        ssh_opts_cpu+=" -i instack_key"
    elif [[ "$INSTALLER_TYPE" == "local" ]] ; then
        if [[ "$COMPUTE_IP" == "none" ]] ; then
            COMPUTE_IP=$(getent hosts "$COMPUTE_HOST" | awk '{ print $1 }')
            if [[ -z "$COMPUTE_IP" ]]; then
                echo "ERROR: Could not resolve $COMPUTE_HOST. Either manually set COMPUTE_IP or enable DNS resolution."
                exit 1
            fi
        fi

        echo "INSTALLER_TYPE set to 'local'. Assuming SSH keys already exchanged with $COMPUTE_HOST"
    fi

    # verify connectivity to target compute host
    ping -c 1 "$COMPUTE_IP"
}

download_image() {
    [ -e "$IMAGE_FILE" ] && return 0
    wget "$IMAGE_URL" -o "$IMAGE_FILE"
}

register_image() {
    glance image-list | grep -q " $IMAGE_NAME " && return 0
    glance image-create --name "$IMAGE_NAME" \
                        --visibility public \
                        --disk-format "$IMAGE_FORMAT" \
                        --container-format bare \
                        --file "$IMAGE_FILE"
}

create_test_user() {
    keystone user-list | grep -q "$TEST_USER" || {
        keystone user-create --name "$TEST_USER" --pass "$TEST_PW"
    }
    keystone tenant-list | grep -q "$TEST_TENANT" || {
        keystone tenant-create --name "$TEST_TENANT"
    }
    keystone user-role-list --user "$TEST_USER" --tenant "$TEST_TENANT" \
    | grep -q "_member_" || {
        keystone user-role-add --user "$TEST_USER" --role _member_  \
                           --tenant "$TEST_TENANT"
    }
}

boot_vm() {
    nova list | grep -q " $VM_NAME " && return 0
    # test VM done with test user, so can test non-admin
    export OS_USERNAME="$TEST_USER"
    export OS_PASSWORD="$TEST_PW"
    export OS_TENANT_NAME="$TEST_TENANT"
    nova boot --flavor "$VM_FLAVOR" \
              --image "$IMAGE_NAME" \
              "$VM_NAME"
    sleep 1
    # back to admin user
    source stackrc
}

create_alarm() {
    ceilometer alarm-list | grep -q " $ALARM_NAME " && return 0
    vm_id=$(nova list | grep " $VM_NAME " | awk '{print $2}')
    ceilometer alarm-event-create --name "$ALARM_NAME" \
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
    while true
    do
        state=$(nova list | grep " $VM_NAME " | awk '{print $6}')
        [[ "$state" == "ACTIVE" ]] && return 0
        sleep 1
    done
}

inject_failure() {
    echo "disabling network of compute host [$COMPUTE_HOST] for 3 mins..."
    cat > disable_network.sh << 'END_TXT'
#!/bin/bash -x
dev=$(ip route | awk '/^default/{print $5}')
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

check_host_status_down() {
    # Switching to test user
    export OS_USERNAME="$TEST_USER"
    export OS_PASSWORD="$TEST_PW"
    export OS_TENANT_NAME="$TEST_TENANT"
    
    host_status_line=$(nova show $VM_NAME | grep "host_status")
    [[ $? -ne 0 ]] && {
        echo "ERROR: host_status not configured for owner in Nova policy.json"
    }
    # back to admin user
    source stackrc
    host_status=$(echo $host_status_line | awk '{print $4}')
    [[ "$host_status" == "DOWN" ]] && {
        echo "$VM_NAME showing host_status: $host_status"
        return 0
    }
    echo "ERROR: host_status not reported by: nova show $VM_NAME"
}

cleanup() {
    set +e
    echo "cleanup..."
    stop_monitor
    stop_inspector
    stop_consumer

    python ./nova_force_down.py "$COMPUTE_HOST" --unset
    sleep 1
    nova delete "$VM_NAME"
    sleep 1
    alarm_id=$(ceilometer alarm-list | grep " $ALARM_NAME " | awk '{print $2}')
    sleep 1
    [ -n "$alarm_id" ] && ceilometer alarm-delete "$alarm_id"
    sleep 1
    image_id=$(glance image-list | grep " $IMAGE_NAME " | awk '{print $2}')
    sleep 1
    [ -n "$image_id" ] && glance image-delete "$image_id"
    keystone user-role-remove --user "$TEST_USER" --role _member_ \
                              --tenant "$TEST_TENANT"
    keystone tenant-remove --name "$TEST_TENANT"
    keystone user-delete "$TEST_USER"

    #TODO: add host status check via nova admin api
    echo "waiting disabled compute host back to be enabled..."
    sleep 180
    ssh $ssh_opts_cpu "$COMPUTE_USER@$COMPUTE_IP" \
        "[ -e disable_network.log ] && cat disable_network.log"
}


echo "Note: doctor/tests/run.sh has been executed."

prepare_compute_ssh

trap cleanup EXIT

echo "preparing VM image..."
download_image
register_image

echo "starting doctor sample components..."
start_monitor
start_inspector
start_consumer

echo "creating test user..."
create_test_user

echo "creating VM and alarm..."
boot_vm
create_alarm
wait_for_vm_launch

sleep 60
echo "injecting host failure..."
inject_failure
sleep 10

check_host_status_down
calculate_notification_time

echo "done"
