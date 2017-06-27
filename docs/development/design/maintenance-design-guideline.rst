.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

====================================
Planned Maintenance Design Guideline
====================================

.. NOTE::
   This is spec draft of design guideline for planned maintenance.
   JIRA ticket to track the update and collect comments: `DOCTOR-52`_.

This document describes how one can implement planned maintenance by utilizing
the `OPNFV Doctor project`_. framework and to meet the set requirements.

Problem Description
===================

Telco application need to know when planned maintenance is going to happen in
order to guarantee zero down time in its operation. It needs to be possible to
make own actions to have application running on not affected resource or give
guidance to admin actions like migration. More details are defined in
requirement documentation: `use cases`_, `architecture`_ and `implementation`_.
Also discussion in the OPNFV summit about `planned maintenance session`_.

Guidelines
==========

Cloud admin needs to make a notification about planned maintenance including
all details that application needs in order to make decisions upon his affected
service. This notification payload can be consumed by application by subscribing
to corresponding event alarm trough alarming service like AODH.

Before maintenance starts application needs to be able to make switch over for
his ACT-STBY service affected, do operation to move service to not effected part
of infra or give a hint for admin operation like migration that can be
automatically issued by admin tool according to agreed policy.

Flow diagram::

  admin alarming project  controller  inspector
    |   service  app manager   |           |
    |  1.   |         |        |           |
    +------------------------->+           |
    +<-------------------------+           |
    |  2.   |         |        |           |
    +------>+    3.   |        |           |
    |       +-------->+   4.   |           |
    |       |         +------->+           |
    |       |    5.   +<-------+           |
    +<----------------+        |           |
    |                 |   6.   |           |
    +------------------------->+           |
    +<-------------------------+     7.    |
    +------------------------------------->+
    |   8.  |         |        |           |
    +------>+    9.   |        |           |
    |       +-------->+        |           |
    +--------------------------------------+
    |                10.                   |
    +--------------------------------------+
    |  11.  |         |        |           |
    +------------------------->+           |
    +<-------------------------+           |
    |  12.  |         |        |           |
    +------>+-------->+        |    13.    |
    +------------------------------------->+
    +-------+---------+--------+-----------+

Concepts used below:

- `full maintenance`: This means maintenance will take a longer time and
  resource should be emptied, meaning container or VM need to be moved or
  deleted. Admin might need to test resource to work after maintenance.

- `reboot`: Only a reboot is needed and admin does not need separate testing
  after that. Container or VM can be left in place if so wanted.

- `notification`: Notification to rabbitmq.

Admin makes a planned maintenance session where he sets a `maintenance_id` that
is a unique ID for all the hardware resources he is going to have the
maintenance at the same time. Mostly maintenance should be done node by node,
meaning a single compute node at a time would be in single planned maintenance
session having unique `maintenance_id`. This ID will be carried trough the whole
session in all places and can be used to query maintenance in admin tool API.
Project running a Telco application should set a specific role for admin tool to
know it cannot do planned maintenance unless project has agreed actions to be
done for its VMs or containers. This means the project has configured itself to
get alarms upon planned maintenance and it is capable of agreeing needed
actions.

The flow of planned maintenance session:

1.  Admin disables nova-compute to do planned maintenance on a compute host and
    gets ACK from the API call. This is regardless the whole compute is affected
    by maintenance to make sure nothing is placed on part need to be maintained.
2.  Admin tool sends a project specific `planned maintenance` notification with
    detailed information about maintenance, like when it is going to start, is
    it `reboot` or `full maintenance` including the information about project
    containers or VMs running on host or the part of it that will need
    maintenance. Also default action like migration will be mentioned that will
    be issued by admin tool before maintenance starts if no other action is set
    by project. In case project has a specific role set, planned maintenance
    cannot start unless project has agreed the admin action. Available admin
    actions are also listed in notification.
3.  Application manager of the project receives AODH alarm about the same.
4.  Application manager can do switch over to his ACT-STBY service, delete and
    re-instantiate his service on not affected resource if so wanted.
5.  Application manager may call admin tool API to give preferred instructions
    for leaving VMs and containers in place or do admin action to migrate them.
    In case admin tool does not receive this instruction before maintenance is
    to start it will do the pre-configured default action like migration to
    projects without a specific role to say project need to agree the action.
    VMs or Containers can be left on host if type of maintenance is just `reboot`.
6.  Admin tool does possible actions to VMs and containers and receives an ACK.
7.  Admin tool cancel `planned maintenance` alarm and send `in maintenance`
    notification. This notification can be consumed by Inspector and other cloud
    services to know there is ongoing maintenance which means things like
    automatic fault management actions for the host should be disabled.
8.  If maintenance type is `reboot` and project is still having containers or
    VMs running on affected hardware resource, Admin tool sends project specific
    `in maintenance` notification.
9.  Application manager of the project receives AODH alarm about the same.
10. Admin will do the maintenance. This is out of Doctor scope.
11. Admin enables nova-compute service when maintenance is over and host can be
    put back to production. An ACK is received from API call.
12. Admin tool cancel possible `in maintenance` alarm.
13. Admin tool send `maintenance over` notification for Inspector and other
    cloud services to know hardware resource is back in use.

POC
---

There was a `Maintenance POC`_ for planned maintenance in the OPNFV Beijing
summit to show the basic concept of using framework defined by the project.

.. _DOCTOR-52: https://jira.opnfv.org/browse/DOCTOR-52
.. _OPNFV Doctor project: https://wiki.opnfv.org/doctor
.. _use cases: http://artifacts.opnfv.org/doctor/docs/requirements/02-use_cases.html#nvfi-maintenance
.. _architecture: http://artifacts.opnfv.org/doctor/docs/requirements/03-architecture.html#nfvi-maintenance
.. _implementation:  http://artifacts.opnfv.org/doctor/docs/requirements/05-implementation.html#nfvi-maintenance
.. _planned maintenance session: https://lists.opnfv.org/pipermail/opnfv-tech-discuss/2017-June/016677.html
.. _Maintenance POC: https://wiki.opnfv.org/download/attachments/5046291/Doctor%20Maintenance%20PoC%202017.pptx?version=1&modificationDate=1498182869000&api=v2
