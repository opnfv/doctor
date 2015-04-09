..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

============================
Notification Alarm Evaluator
============================

https://blueprints.launchpad.net/ceilometer/+spec/notification-alarm-evaluator

This blueprint proposes to add a new alarm evaluator for handling alarms on
events passed from other OpenStack services, that provides event-driven alarm
evaluation which makes new sequence in Ceilometer instead of the polling-based
approach of the existing Alarm Evaluator, and realizes immediate alarm
notification to end users.

Problem description
===================

As an end user, I need to receive alarm notification immediately once
Ceilometer captured an event which would make alarm fired, so that I can
perform recovery actions promptly to shorten downtime of my service.
The typical use case is that an end user set alarm on "compute.instance.update"
in order to trigger recovery actions once the instance status has changed to
'shutdown' or 'error'.

The existing Alarm Evaluator is periodically querying/polling the databases
in order to check all alarms independently from other processes. This is good
approach for evaluating an alarm on samples stored in a certain period.
However, this is not efficient to evaluate an alarm on events which are emitted
by other OpenStack servers once in a while.

The periodical evaluation leads delay on sending alarm notification to users.
The default period of evaluation cycle is 60 seconds. It is recommended that
an operator set longer interval than configured pipeline interval for
underlying metrics, and also longer enough to evaluate all defined alarms
in certain period while taking into account the number of resources, users and
alarms.

Proposed change
===============

The proposal is to add a new event-driven alarm evaluator which receives
messages from Notification Agent and finds related Alarms, then evaluates each
alarms;

* New alarm evaluator could receive event notification from Notification Agent
  by which adding a dedicated notifier as a publisher in pipeline.yaml
  (e.g. notifier://?topic=event_eval).

* When new alarm evaluator received event notification, it queries alarm
  database by Project ID and Resource ID written in the event notification.

* Found alarms are evaluated by referring event notification.

* Depending on the result of evaluation, those alarms would be fired through
  Alarm Notifier as the same as existing Alarm Evaluator does.

This proposal also adds new alarm type "notification" and "notification_rule".
This enables users to create alarms on events. The separation from other alarm
types (such as "threshold" type) is intended to show different timing of
evaluation and different format of condition, since the new evaluator will
check each event notification once it received whereas "threshold" alarm can
evaluate average of values in certain period calculated from multiple samples.

The new alarm evaluator handles Notification type alarms, so we have to change
existing alarm evaluator to exclude "notification" type alarms from evaluation
targets.

Alternatives
------------

There was similar blueprint proposal "Alarm type based on notification", but
the approach is different. The old proposal was to adding new step (alarm
evaluations) in Notification Agent every time it received event from other
OpenStack services, whereas this proposal intends to execute alarm evaluation
in another component which can minimize impact to existing pipeline processing.

Another approach is enhancement of existing alarm evaluator by adding
notification listener. However, there are two issues; 1) this approach could
cause stall of periodical evaluations when it receives bulk of notifications,
and 2) this could break the alarm portioning i.e. when alarm evaluator received
notification, it might have to evaluate some alarms which are not assign to it.

Data model impact
-----------------

Resource ID will be added to Alarm model as an optional attribute.
This would help the new alarm evaluator to filter out non-related alarms
while querying alarms, otherwise it have to evaluate all alarms in the project.

REST API impact
---------------

Alarm API will be extended as follows;

* Add "notification" type into alarm type list
* Add "resource_id" to "alarm"
* Add "notification_rule" to "alarm"

Sample data of Notification-type alarm::

  {
      "alarm_actions": [
          "http://site:8000/alarm"
      ],
      "alarm_id": null,
      "description": "An alarm",
      "enabled": true,
      "insufficient_data_actions": [
          "http://site:8000/nodata"
      ],
      "name": "InstanceStatusAlarm",
      "notification_rule": {
          "event_type": "compute.instance.update",
          "query" : [
              {
                  "field" : "traits.state",
                  "type" : "string",
                  "value" : "error",
                  "op" : "eq",
              },
          ]
      },
      "ok_actions": [],
      "project_id": "c96c887c216949acbdfbd8b494863567",
      "repeat_actions": false,
      "resource_id": "153462d0-a9b8-4b5b-8175-9e4b05e9b856",
      "severity": "moderate",
      "state": "ok",
      "state_timestamp": "2015-04-03T17:49:38.406845",
      "timestamp": "2015-04-03T17:49:38.406839",
      "type": "notification",
      "user_id": "c96c887c216949acbdfbd8b494863567"
  }

"resource_id" will be refered to query alarm and will not be check permission
and belonging of project.

Security impact
---------------

None

Pipeline impact
---------------

None

Other end user impact
---------------------

None

Performance/Scalability Impacts
-------------------------------

"resource_id" can be optional, but restricting it to mandatory could be reduce
performance impact. If user create "notification" alarm without "resource_id",
those alarms will be evaluated every time event occurred in the project.
That may lead new evaluator heavy.

Other deployer impact
---------------------

New service process have to be run.

Developer impact
----------------

Developers should be aware that events could be notified to end users and avoid
passing raw infra information to end users, while defining events and traits.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  r-mibu

Other contributors:
  None

Ongoing maintainer:
  None

Work Items
----------

* New event-driven alarm evaluator

* Add new alarm type "notification" as well as AlarmNotificationRule

* Add "resource_id" to Alarm model

* Modify existing alarm evaluator to filter out "notification" alarms

* Add new config parameter for alarm request check whether accepting alarms
  without specifying "resource_id" or not

Future lifecycle
================

This proposal is key feature to provide information of cloud resources to end
users in real-time that enables efficient integration with user-side manager
or Orchestrator, whereas currently those information are considered to be
consumed by admin side tool or service.
Based on this change, we will seek orchestrating scenarios including fault
recovery and add useful event definition as well as additional traits.

Dependencies
============

None

Testing
=======

New unit/scenario tests are required for this change.

Documentation Impact
====================

* Proposed evaluator will be described in the developer document.

* New alarm type and how to use will be explained in user guide.

References
==========

* OPNFV Doctor project: https://wiki.opnfv.org/doctor

* Blueprint "Alarm type based on notification":
  https://blueprints.launchpad.net/ceilometer/+spec/alarm-on-notification
