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
COMPUTE_HOST=${COMPUTE_HOST:-none}
ssh_opts="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

if [[ "$INSTALLER_TYPE" != "apex" ]] ; then
    echo "ERROR: INSTALLER_TYPE=$INSTALLER_TYPE is not supported."
    exit 1
fi

if [[ "$INSTALLER_IP" == "none" ]] ; then
    instack_mac=$(sudo virsh domiflist instack | awk '/default/{print $5}')
    INSTALLER_IP=$(/usr/sbin/arp -e | grep ${instack_mac} | awk '{print $1}')
fi

if [[ "$COMPUTE_HOST" == "none" ]] ; then
    COMPUTE_HOST=$(sudo ssh $ssh_opts $INSTALLER_IP \
                   "source stackrc; \
                    nova show overcloud-novacompute-0 \
                    | awk '/ ctlplane network /{print \$5}'")
fi

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
    sudo python monitor.py "$COMPUTE_HOST" "http://127.0.0.1:$INSPECTOR_PORT/events" > monitor.log 2>&1 &
    MONITOR_PID=$!
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
sleep 180
echo sudo ip link set $dev up
sleep 1
END_TXT
    chmod +x disable_network.sh
    sudo scp $ssh_opts disable_network.sh $INSTALLER_IP:
    ssh_opts_cpu="$ssh_opts -i /home/stack/.ssh/id_rsa"
    sudo ssh $ssh_opts $INSTALLER_IP \
        "scp $ssh_opts_cpu disable_network.sh heat-admin@$COMPUTE_HOST: && \
         ssh $ssh_opts_cpu 'nohup ./disable_network.sh > c 2>&1 &'"
}

calculate_notification_time() {
    detect=$(grep "doctor monitor detected at" monitor.log | awk '{print $5}')
    notified=$(grep "doctor consumer notified at" consumer.log | awk '{print $5}')
    duration=$(echo "$notified $detect" | awk '{print $1 - $2 }')
    echo "$notified $detect" | \
        awk '{d = $1 - $2; if (d < 1 ) print d " OK"; else print d " NG"}'
}

echo "Note: doctor/tests/run.sh has been executed."
exit 0

download_image
register_image

start_monitor
start_inspector
start_consumer

boot_vm
create_alarm
wait_for_vm_launch

sleep 60
inject_failure
sleep 10

calculate_notification_time

echo "done"
