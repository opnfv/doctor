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

.. figure:: images/figure-p1.png
    :name: figure-p1
    :width: 100%

    Doctor platform and typical sequence (Brahmaputra)

Detailed information on the Doctor architecture can be found in the Doctor
requirements documentation:
http://artifacts.opnfv.org/doctor/docs/requirements/05-implementation.html


Use case
""""""""

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

The "run-sh" script will execute the following commands::

 140 start_monitor
 141 start_inspector
 142 start_consumer
 143 
 144 boot_vm
 145 create_alarm
 146 wait_for_vm_launch
 147 
 148 sleep 60
 149 inject_failure
 150 sleep 10
 151 
 152 calculate_notification_time
  
First the Doctor components are started, the VM is booted, and an alarm event
is created in Ceilometer::

create_alarm() {
  50     ceilometer alarm-list | grep -q " $ALARM_NAME " && return 0
  51     vm_id=$(nova list | grep " $VM_NAME " | awk '{print $2}')
  52     ceilometer alarm-event-create --name "$ALARM_NAME" \
  53         --alarm-action "http://localhost:$CONSUMER_PORT/failure" \
  54         --description "VM failure" \
  55         --enabled True \
  56         --repeat-actions False \
  57         --severity "moderate" \
  58         --event-type compute.instance.update \
  59         -q "traits.state=string::error; traits.instance_id=string::$vm_id"
  60 }
  
After sleeping for 1 minute in order to wait for the VM launch to complete,
a failure is injected to the system, i.e. the network of comupte host is
disabled for 3 minutes.

Finally, the notification time, i.e. the time between the execution of step 2
(Monitor detected failure) and step 9 (Consumer received failure notification)
is calculated::

 122 calculate_notification_time() {
 123     detect=$(grep "doctor monitor detected at" monitor.log | awk '{print $5}')
 124     notified=$(grep "doctor consumer notified at" consumer.log | awk '{print $5}')
 125     duration=$(echo "$notified $detect" | awk '{print $1 - $2 }')
 126     echo "$notified $detect" | \
 127         awk '{d = $1 - $2; if (d < 1 ) print d " OK"; else print d " NG"}'
 128 }

 According to the Doctor requirements, the Doctor test is successful if the
 notification time is below 1 second.

Authors
""""""""

co-author:
	Gerald Kunzmann
