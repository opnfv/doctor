#!/bin/bash -ex
#
# Copyright 2016 NEC Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

IMAGE_URL=https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
IMAGE_NAME=cirros
IMAGE_FILE="${IMAGE_NAME}.img"
IMAGE_FORMAT=qcow2
VM_NAME=doctor_vm1
VM_FLAVOR=m1.tiny
ALARM_NAME=doctor_alarm1
INSPECTOR_PORT=12345
CONSUMER_PORT=12346

# NOTE: You have to be changed these paramas depends on your machine,
#       installer and configs.
COMPUTE_HOST='192.0.2.8'
SSH_TO_COMPUTE_HOST="ssh heat-admin@$COMPUTE_HOST"


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
    $SSH_TO_COMPUTE_HOST "
cat > disable_network.sh << 'END_TXT'
#!/bin/bash
dev=\$(/usr/sbin/ip route | awk '/^default/{print \$5}')
sleep 1
echo sudo ip link set \$dev down
sleep 180
echo sudo ip link set \$dev up
sleep 1
END_TXT
chmod +x disable_network.sh
nohup ./disable_network.sh > c 2>&1 &"
}

calculate_notification_time() {
    detect=$(grep "doctor monitor detected at" monitor.log | awk '{print $5}')
    notified=$(grep "doctor consumer notified at" consumer.log | awk '{print $5}')
    duration=$(echo "$notified $detect" | awk '{print $1 - $2 }')
    echo "$notified $detect" | \
        awk '{d = $1 - $2; if (d < 1 ) print d " OK"; else print d " NG"}'
}

# TODO(r-mibu): Make sure env params are set properly for OpenStack clients
# TODO(r-mibu): Make sure POD for doctor test is available in Pharos

echo "Note: doctor/tests/run.sh has been executed, "
echo "      but skipping this test due to lack of available test env/deployment."
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
