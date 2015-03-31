====================================================
Report host fault to update server state immediately
====================================================

https://blueprints.launchpad.net/nova/+spec/update-server-state-immeinletdiately

When a server goes down because of a host hardware, OS or hypervisor error, the server state remains as operational in OpenStack API.

A new API is needed to report a host fault to change the state of the servers and services immediately.

The new API provides the possibility for external monitoring system to detect any kind of host failure fast and reliably and inform OpenStack about it. External tool also fences the host. Nova updates the host state and also updates state of the effected servers on the host. This way the host and server state in Nova DB will be in synch with the real state of the system.

Problem description
===================
* Nova state change for failed or unreachable host is slow and does not reliably state host is down or not. This might cause same server instance to run twice if action taken to evacuate instance to another host.
* Nova state for server(s) on failed host will not change, but remains active and running. This gives user a false information about server state. Currently one would need to call "nova reset-state" for each VM to have them to error state.
* Openstack user cannot make HA actions fast and reliably by trusting server state and host state.

Use Cases
----------
Use case in general is that in case there is a host fault one should change host state fast and reliably when using DB servicegroup backend. On top of this here is the use cases that are not covered currently to have server states changed correctly:
* Management network connectivity lost between controller and compute node.
* Host HW failed.

Generic use case flow:
* The external monitoring system detects a host fault.
* The external monitoring system fences the  host if not down already.
* The external system calls the new Nova API to force the failed host into down state as well as servers running on it.
* Nova updates the host state and state of the effected servers to Nova DB.

Currently nova-compute state will be changing "down", but it takes a long time. Server state keeps as "vm_state: active" and "power_state: running", which is not correct. By having external tool to detect host faults fast, fence host by powering down and then report host down to OpenStack, all these states would reflect to actual situation. Also if OpenStack will not implement automatic actions for fault correlation, external tool can do that.
This could be configured for example in server instance METADATA easily and be read by external tool.

Project Priority
-----------------
Liberty priorities have not yet been defined.

Proposed change
===============
There needs to be a new API for Admin to state host is down. This API is used to mark services running in host down to reflect the real situation.

Example on compute node is:

* When compute node is up and running:
  vm_state: activeand power_state: running
  nova-compute state: up status: enabled
* When compute node goes down and new API is called to state host is down:
  vm_state: stopped power_state: shutdown
  nova-compute state: down status: enabled

  vm_state values: soft-delete, deleted, resized and error should not be touched.
  task_state effect needs to be worked out.

Alternatives
------------
There is no attractive alternatives to detect all different host faults than to have a external tool to detect different host faults. For this kind of tool to exist there needs to be new API in Nova to report fault. Currently there must have been some kind of workarounds implemented as cannot trust or get the states from OpenStack fast enough.

Data model impact
-----------------
None

API impact
----------
* Update CLI to report host is down:

 ``nova host-update command``

 ``usage: nova host-update [--status <enable|disable>]``
 ``[--maintenance <enable|disable>]``
 ``[--report-host-down]``
 ``<hostname>``
 Update host settings.

 Positional arguments

 ``<hostname>``
 Name of host.

 Optional arguments

 ``--status <enable|disable>``
 Either enable or disable a host.

 ``--maintenance <enable|disable>``
 Either put or resume host to/from maintenance.

 ``--down``
 Report host down to update service and server state in db.

* Update Compute API to report host is down:

 ``/v2.1/{tenant_id}/os-hosts/{host_name}``

 Normal response codes: 200
 Request parameters

 Parameter     Style   Type          Description
 host_name     URI     xsd:string      The name of the host of interest to you.

 ``{``
 ``  "host": {``
 ``    "status": "enable",``
 ``    "maintenance_mode": "enable"``
 ``    "host_down_reported": "true"``
 ``  }``
 ``}``

 ``{``
 ``  "host": {``
 ``    "host": "65c5d5b7e3bd44308e67fc50f362aee6",``
 ``    "maintenance_mode": "enabled",``
 ``    "status": "enabled"``
 ``    "host_down_reported": "true"``
 ``  }``
 ``}``

* New method to nova.compute.api module HostAPI class to have a to mark host related server(s) and service(s) down:

 ``set_host_down(context, host_name)``

* class novaclient.v2.hosts.HostManager(api) method update(host, values)

 Needs to handle reporting host down.

* Schema does not need changes as in db only service and server states are to be changed.

Security impact
---------------
API call needs admin privileges (in the default policy configuration).

Notifications impact
--------------------
None

Other end user impact
---------------------
None

Performance Impact
------------------
Only impact is that user can get information faster. No impact that would slow down. Host down should be rare occurrence. Single call of API should find all servers and services running on host and change state.

Other deployer impact
---------------------
Developer can make use of any external tool to detect host fault and report it to OpenStack.

Developer impact
----------------
None

Implementation
==============
Assignee(s)
-----------
Primary assignee:   Tomi Juvonen

Other contributors: Ryota Mibu

Work Items
----------
* Test cases.
* API changes.
* Documentation.

Dependencies
============
None

Testing
=======
Test cases that exists for enabling or putting host to maintenence should be altered or similar new cases made test new functionality.

Documentation Impact
====================
New API needs to be documented:

* Compute API extensions documentation.
  http://developer.openstack.org/api-ref-compute-v2.1.html
* Nova commands documentation.
  http://docs.openstack.org/user-guide-admin/content/novaclient_commands.html
* Compute command-line client documentation.
  http://docs.openstack.org/cli-reference/content/novaclient_commands.html
* nova.compute.api documentation.
  http://docs.openstack.org/developer/nova/api/nova.compute.api.html
* High Availability guide might have page to tell external tool could provide ability to provide faster HA as able to update states by new API.
  http://docs.openstack.org/high-availability-guide/content/index.html

References
==========
* OPNFV Doctor project: https://wiki.opnfv.org/doctor
* OpenStack Instance HA Proposal:
  http://blog.russellbryant.net/2014/10/15/openstack-instance-ha-proposal/
* The Different Facets of OpenStack HA:
  http://blog.russellbryant.net/2015/03/10/the-different-facets-of-openstack-ha/

==============================================================
Blueprints for discussion in tech-discuss meeting (March 19)
==============================================================

see Figure 1: https://wiki.opnfv.org/_media/doctor/opnfv_doctor_blueprints.png

The following definitions are used:
  "Event" is a message emitted by other OpenStack services such as Nova and Neutron and are consumed by the "Notification Agents" in Ceilometer.
  "Notification" is a message generated by a "Notification Agent" in Ceilometer based on an "event" and is delivered to the "Collectors" in Ceilometer that store those notifications (as "sample") to the Ceilometer "Databases".

Doctor project is planning to handle "events" and "notifications" regarding Resource Status; Instance State, Port State, Host State, etc. :

 Currently, Ceilometer already receives "events" to identify the state of those resources, but it does not handle and store them yet. This is why we also need a new event definition to capture those resource states from "events" created by other services.
 Note, the definitions of new events/notifications are not included in these BPs, but will be proposed subsequently in additional BPs.

Alignment of blueprints with HA project has been clarified, see https://wiki.opnfv.org/_media/doctor/opnfv_ceilometer_bp_alignment.20150306.pptx for detail.

Event Publisher for Alarm (Ceilometer)
* Problem statement:

The existing “Alarm Evaluator” in OpenStack Ceilometer is periodically querying/polling the databases in order to check all alarms independently from other processes. This is adding additional delay to the fault notification send to the Consumer, whereas one requirement of Doctor is to react on faults as fast as possible.

The existing message flow is shown in  Figure 1: after receiving an "event", a "notification agent" (i.e. "event publisher") will send a "notification" to a "Collector". The "collector" is collecting the notifications and is updating the Ceilometer "Meter" database that is storing information about the "sample" which is capured from original "event". The "Alarm Evaluator" is periodically polling this databases then querying "Meter" database based on each alarm configuration.

In current Ceilometer implementation, there is no possibility to directly trigger the "Alarm Evaluator" when a new "event" was received, but the "Alarm Evaluator" will only find out that requires firing new notification to the Consumer when polling the database.

* Change/feature request:

This BP proposes to add a new "event publisher for alarm", which is bypassing several steps in Ceilometer in order to avoid the polling-based approach of the existing Alarm Evaluator that makes notification slow to users.

After receiving an "(alarm) event" by listening on the Ceilometer message queue ("notification bus"), the new "event publisher for alarm" immediately hands a "notification" about this event to a new Ceilometer component "Notification-driven alarm evaluator" proposed in the other BP.

Note, the term "publisher" refers to an entity in the Ceilometer architecture (it is an "notification agent"). It offers the capability to provide notifications to other services outside of Ceilometer, but it is also used to deliver notifications to other Ceilometer components (e.g. the "Collectors") via the Ceilometer "notification bus".

* Implementation detail

* "event publisher for alarm" is part of Ceilometer

* The standard AMQP message queue is used with a new topic string.

* No new interfaces have to be added to Ceilometer.

* "Event publisher for Alarm" can be configured by the Administrator of Ceilometer to be used as "Notification Agent" in addition to the existing "Notifier"

* Existing alarm mechanisms of Ceilometer can be used allowing users to configure how to distribute the "notifications" transformed from "events", e.g. there is an option whether an ongoing alarm is re-issued or not ("repeat_actions").

* Name of the blueprint/implementation owner: Ryota Mibu (NEC)

The current blueprint submitted to OpenStack reads as follow:
The proposal is to create a new event publisher which can send messages to a new alarm evaluator (see Section 5.6.3). The publisher enables Ceilometer to provide event driven notifications to the user. Besides the existing Ceilometer usage for billing purposes, this BP enhances Ceilometer to provide additional notification capabilities to the user.
Notification-driven alarm evaluator (Ceilometer)
* Problem statement:

The existing “Alarm Evaluator” in OpenStack Ceilometer is periodically querying/polling the databases in order to check all alarms independently from other processes. This is adding additional delay to the fault notification send to the Consumer, whereas one requirement of Doctor is to react on faults as fast as possible.

* Change/feature request:

This BP is proposing to add an alternative "Notification-driven Alarm Evaluator" for Ceilometer that is receiving "notifications" sent by the "Event Publisher for Alarm" described in the other BP.

Once this new “Notification-driven Alarm Evaluator” received "notification", it finds "alarm" configurations which may relate to the "notification" by querying the "alarm" database with some keys i.e. resource ID, then it will evaluate each alarm with the information in that "notification".

After the alarm evaluation, it will perform the same way as the existing "alarm evaluator" does for firing alarm notification to consumer.

Similar to the existing Alarm Evaluator, this new “Notification-driven Alarm Evaluator” is aggregating and correlating different alarms which are then provided northbound to the Consumer via the OpenStack “Alarm Notifier”.

The user/administrator can register the alarm configuration via existing Ceilometer API. Thereby, he can configure whether to set an alarm or not and where to send the alarms to. ( https://wiki.openstack.org/wiki/Ceilometer/Alerting )

* Implementation detail

* The new "Notification-driven Alarm Evaluator" is part of Ceilometer.

* Most of the existing source code of the “Alarm Evaluator” can be re-used to implement this BP

* No additional application logic is needed

* It will access the Ceilometer Databases just like the existing "Alarm evaluator"

* Only the polling-based approach will be replaced by a listener for "notifications" provided by the "Event Publisher for Alarm" on the Ceilometer "notification bus".

* No new interfaces have to be added to Ceilometer.

* Name of the blueprint/implementation owner; Ryota Mibu (NEC)


The blueprint submitted to OpenStack reads as follow:
This BP proposes a notification-driven alarm evaluator that is using event notifications received from a "event publisher for alarm" (see Section 5.6.2). The alarm evaluator does not execute any periodical task, but is triggered by alarm notifications. The alarm evaluator will aggregate and correlate different alarms, which will then be notified to the user in order to trigger recovery action(s) on the user-side (e.g. migrate, terminate, re-instantiate etc.).
---------------------------------------------------
Blueprint Planning [Under Construction]

Ceilometer

BP#1 Instance State Notification

This BP proposes to add a new compute notification state entry to handle instance events which are emitted from nova. It also creates a new meter "instance.state".

The BP focuses on creating the metric "instance.state" by using a notification agent rather than a polling based approach, as it would be used with a "event publisher for alarm" [BP#2].

BP#2 Event Publisher for Alarm

The proposal is to create a new event publisher which can send messages to a new "notification-driven alarm evaluator" [BP#3].

The publisher enables Ceilometer to provide event driven notifications to the user.

Besides the existing Ceilometer usage for billing purposes, this BP enhances Ceilometer to provide additional notification capabilities to the user.

BP#3 Notification-driven alarm evaluator

This BP proposes a notification-driven alarm evaluator that is using event notifications received from a "event publisher for alarm" [BP#2].

The alarm evaluator does not execute any periodical task, but is triggered by alarm notifications.

The alarm evaluator will aggregate and correlate different alarms, which will then be notified to the user in order to trigger recovery action(s) on the user-side (e.g. migrate, terminate, re-instantiate etc.).

[HA] BP#4 SNMP notifier to user (NBI)

[HA] BP#5 Real-time Alarm (table)

[HA] BP#6-New plugin for Detector

(othermissing event/meter/notification definitions)

Nova

BP#1 Report host fault to update server state immediately.

When a server goes down because of an host hardware, OS or hypervisor error, the server state remains as operational in OpenStack API.

A new API is needed to report that a host fault and to change the state of the server(s) immediately.

The new API provides the possibility to externally detect any kind of host failure and to inform OpenStack about it.

https://blueprints.launchpad.net/nova/+spec/update-server-state-immediately

Note: See also https://wiki.opnfv.org/_media/doctor/opnfv_ceilometer_bp_alignment.20150305.pptx .
https://wiki.opnfv.org/_media/opnfv-doctor-nova-blueprint.pptx.
---
posted / related blueprints:

BP#1-#3 https://blueprints.launchpad.net/ceilometer/+spec/realtime-alarm-management (see above) [submitted by Doctor project]

OpenStack Ceilometer already provides some functionality to monitor and alert the user about faults in the server. It will be useful to enhance this functionality as follows:

[1] Instance State Notification

This BP proposes adding new compute notification definition regarding instance state to handle event of instance (server) from nova.

It also enables to create a new meter "instance.state".

To notify an instance.state change immediately, the BP creates "instance.state" by using the notification agent rather than the pollster.

[2] Event Publisher for Alarm

The proposal is to create a new event publisher which can send messages to a new alarm evaluator [3].

The publisher enables the admin to provide event driven notifications to users such that they can achieve fast auto-healing by using this immediate notification mechanism and orchestrator with auto scaling rules.

Besides the existing Ceilometer usage for billing purposes, this BP enhances Ceilometer to provide additional notification capabilities to the user.

[3] Notification-driven alarm evaluator

This BP proposes a notification-driven alarm evaluator that is using event notifications received from [2].

The alarm evaluator does not execute any periodical task, but is triggered by alarm notifications.

The alarm evaluator will aggregate and correlate different alarms, which will then be notified to the user in order to trigger recovery action(s) on the user-side (e.g. migrate, terminate,re-instantiate etc.).

BP#1-#3 https://blueprints.launchpad.net/ceilometer/+spec/add-independent-alarm-mechanism [submitted by HA project][this BP doesn't show implementation specific details]

Openstack need to add an independent fault alarm mechanism to facilitate the user to detect system problems. Alarm mechanism is currently provided in Ceilometer, but can not fully meet the requirements:

1. Ceilometer Alarm main objective is to single or multiple meter set thresholds to trigger heat autoscaling. For non-meter types of failures triggered alarms can not support.

2. Alarm is achieved by periodically polling meter value whether the user-defined threshold is reached, which can not meet the real-time requirements.

3. After triggering Alarm, there are two form of actions: http callback, log. Need to provide a real-time reporting method, such as SNMP interface.

BP#2-#3 https://blueprints.launchpad.net/ceilometer/+spec/alarm-on-notification [abbandoned BP older than OPNFV]

Add a new alarm type that will be triggered when an notification of a certain type and with some fields is received by Ceilometer.

pacemaker-servicegroup-driver

New API to report host fault might be very nice. Any external tool (like Doctor), could detect host error fast and use the API to mark host faulty (and fence the host by shutting down if needed). Anyhow this new API might not get so easily trough to openstack. For this there is already work to get pacemaker servicegroup driver to have host state change fast:

https://blueprints.launchpad.net/nova/+spec/pacemaker-servicegroup-driver.

For server state might have BP to see the host state when querying the server. Now if host state is changed faster, this might fulfill VNFM needs (with current way openstack works), before there is new NB IF in place (to report host faults) as that implementation might take longer as more complicated issue.

LibvirtWatchdog#Notifications

Related info about watchdog devices, quoting from BP [x]: "This is useful to cloud users to deal with problems in their guest OS, to kill off a mis-behaving instance to allow an external HA solution to move processing to another instance."

This BP is in status completed but the notification part that never got implemented. The intention I guess was that the nova-compute libvirt driver should also subscribe to WATCHDOG events from libvirt. nova-compute libvirt driver today is subscribed to LIFECYCLE events. I mention this because watchdog notifications are a topic in the ETSI REL spec.

So I guess some nova BP is also needed to add more libvirt notifications into nova compute libvirt driver?

https://wiki.openstack.org/wiki/LibvirtWatchdog#Notifications

Providing VNF faults through VIM could be helpful.

I think you can propose nova to make nova-compute subscribe to WATCHDOG events from libvirt and emit those events to Ceilometer.

It might be nice that user can express whether monitoring required by selecting flag in flavor or image property to reduce unnecessary notification in operator perspective.

