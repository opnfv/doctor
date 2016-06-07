.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Doctor
^^^^^^

Platform overview
"""""""""""""""""

Doctor platform, as of Brahmaputra release, provides the two features:

* Immediate Notification
* Consistent resource state awareness (Compute/host-down)

These features enable high availability of Network Services on top of
the virtualized infrastructure. Immediate notification allows VNF managers
(VNFM) to process recovery actions promptly once a failure has occurred.
Consistency of resource state is necessary to properly execute recovery
actions properly in the VIM.

The Doctor platform consists of the following components:

* OpenStack Compute (Nova)
* OpenStack Telemetry (Ceilometer)
* OpenStack Alarming (Aodh)
* Doctor Inspector
* Doctor Monitor

.. note::
    Doctor Inspector and Monitor are sample implementations for reference.

You can see an overview of the Doctor platform and how components interact in
:numref:`figure-p1`.

.. figure:: /platformoverview/images/figure-p1.png
    :name: figure-p1
    :width: 100%

    Doctor platform and typical sequence (Brahmaputra)

Detailed information on the Doctor architecture can be found in the Doctor
requirements documentation:
http://artifacts.opnfv.org/doctor/docs/requirements/05-implementation.html


Use case
""""""""

* Controller(Nova) detects faults in the NVFI affecting the proper functioning
  of the virtual resources running on top of it.

The detected faults need to be configured by consumer. Once some faults are
detected, Inspector will check out the resource map maintained by Controller,
to find out which virtual resources are affected and then update the resources
state. Notifier will receive the failure event requests sended from Controller,
and notify the faults to the Consumer according to the alarm configuration.

Detailed workflow inforamtion is as follows:

* Consumer(VNFM): (step 0) create resources (network, server/instance) and an
  event alarm on state down notification of that server/instance

* Monitor: (step 1) periodic ping check from/to each dplane nic to/from gw
  node, (step 2) once it failed send out event with raw machine info to
  Inspector

* Inspector: when it receives an event, it will (step 3) mark the host down
  ("mark-host-down"), (step 4) map the PM to VM, and change the VM status to
  down

* Controller: (step5) send out instance update event to ceilometer

* Notifier: (step 6) Ceilometer transforms and passes that event to aodh,
  (step 7) Aodh will evaluate event with the registered alarm definitions,
  then (step 8) it will fire the alarm to the "consumer" who owns the
  instance

* Consumer(VNFM): (step 9) received the event and (step 10) recreates a new
  instance

Test case
"""""""""

The "run.sh" script will execute the following commands.
::

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

First the Doctor components are started, the VM is booted, and an alarm event
is created in Ceilometer.
::

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

After sleeping for 1 minute in order to wait for the VM launch to complete,
a failure is injected to the system, i.e. the network of comupte host is
disabled for 3 minutes.

Finally, the notification time, i.e. the time between the execution of step 2
(Monitor detected failure) and step 9 (Consumer received failure notification)
is calculated::

     calculate_notification_time() {
         detect=$(grep "doctor monitor detected at" monitor.log | awk '{print $5}')
         notified=$(grep "doctor consumer notified at" consumer.log | awk '{print $5}')
         duration=$(echo "$notified $detect" | awk '{print $1 - $2 }')
         echo "$notified $detect" | \
             awk '{d = $1 - $2; if (d < 1 ) print d " OK"; else print d " NG"}'
     }

According to the Doctor requirements, the Doctor test is successful if the
notification time is below 1 second.

Authors
""""""""

co-author:
     Gerald Kunzmann

other contributors:
     Yuanzhen Li