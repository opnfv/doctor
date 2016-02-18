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

INSTALLER_TYPE=${INSTALLER_TYPE:-apex}
INSTALLER_IP=${INSTALLER_IP:-none}
COMPUTE_HOST=${COMPUTE_HOST:-overcloud-novacompute-0}
COMPUTE_IP=${COMPUTE_IP:-none}
ssh_opts="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

if [[ "$INSTALLER_TYPE" != "apex" ]] ; then
    echo "ERROR: INSTALLER_TYPE=$INSTALLER_TYPE is not supported."
    exit 1
fi

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

prepare_compute_ssh() {
    ping -c 1 "$COMPUTE_IP"

    # get ssh key from installer node
    sudo scp $ssh_opts /home/stack/.ssh/id_rsa instack_key
    if [ ! -r instack_key ]; then
        sudo chown $(whoami):$(whoami) instack_key
    fi
    chmod 400 instack_key
    ssh_opts_cpu="$ssh_opts -i instack_key -l heat-admin"
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

boot_vm() {
    nova list | grep -q " $VM_NAME " && return 0
    nova boot --flavor "$VM_FLAVOR" \
              --image "$IMAGE_NAME" \
              "$VM_NAME"
    sleep 1
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
    echo "disabling network of comupte host [$COMPUTE_HOST] for 3 mins..."
    cat > disable_network.sh << 'END_TXT'
#!/bin/bash -x
dev=$(/usr/sbin/ip route | awk '/^default/{print $5}')
sleep 1
echo sudo ip link set $dev down
sleep 120
echo sudo ip link set $dev up
sleep 1
END_TXT
    chmod +x disable_network.sh
    scp $ssh_opts_cpu disable_network.sh "$COMPUTE_IP:"
    ssh $ssh_opts_cpu "$COMPUTE_IP:" 'nohup ./disable_network.sh > disable_network.log 2>&1 &'
}

calculate_notification_time() {
    detect=$(grep "doctor monitor detected at" monitor.log | awk '{print $5}')
    notified=$(grep "doctor consumer notified at" consumer.log | awk '{print $5}')
    duration=$(echo "$notified $detect" | awk '{print $1 - $2 }')
    echo "$notified $detect" | \
        awk '{d = $1 - $2; if (d < 1 ) print d " OK"; else print d " NG"}'
}

cleanup() {
    set +e
    echo "cleanup..."
    stop_monitor
    stop_inspector
    stop_consumer
    ssh $ssh_opts_cpu $COMPUTE_IP \
        "[ -e disable_network.log ] && cat disable_network.log"

    nova service-force-down --unset "$COMPUTE_HOST" nova-compute
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
    #TODO: add host status check via nova admin api
    echo "waiting disabled compute host back to be enabled..."
    sleep 180
}


echo "Note: doctor/tests/run.sh has been executed."

prepare_compute_ssh

trap cleanup ERR

echo "preparing VM image..."
download_image
register_image

echo "starting doctor sample components..."
start_monitor
start_inspector
start_consumer

echo "creating VM and alarm..."
boot_vm
create_alarm
wait_for_vm_launch

sleep 60
echo "injecting host failure..."
inject_failure
sleep 10

calculate_notification_time

cleanup

echo "done"
