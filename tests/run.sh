#!/bin/bash -ex

#branch=$(git rev-parse --abbrev-ref HEAD)
BRANCH=master

IMAGE_URL=https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
IMAGE_NAME=cirros
IMAGE_FILE="${IMAGE_NAME}.img"
IMAGE_FORMAT=qcow2
VM_NAME=doctor_vm1
VM_FLAVOR=m1.tiny
COMPUTE_HOST='s142'
ALARM_NAME=doctor_alarm1
INSPECTOR_PORT=12345
CONSUMER_PORT=12346


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
    #FIXME
    echo ssh $COMPUTE_HOST "ip link set eno1 down"
}

calculate_notification_time() {
    detect=$(grep "doctor monitor detected at" | awk '{print $5}')
    notified=$(grep "doctor consumer notified at" | awk '{print $5}')
    duration=$(echo "$notified $detect" | awk '{print $1 - $2 }')
    echo "$notified $detect" | \
        awk '{d = $1 - $2; if (d < 1 ) print d " OK"; else print d " NG"}'
}

# FIXME
set +x
source /opt/stack/devstack/openrc admin admin
set -x

download_image
register_image

start_monitor
start_inspector
start_consumer

boot_vm
create_alarm
wait_for_vm_launch

sleep 61
inject_failure

calculate_notification_time

echo "done"
