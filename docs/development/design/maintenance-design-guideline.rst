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
to corresponding event alarm trough AODH.

Before maintenance starts application needs to be able to make switch over for
his ACT-STBY service affected, do operation to move service to not effected part
of infra or give a hint for admin operation like migration that can be
automatically issued by admin tool according to agreed policy.

Flow diagram::

  admin   AODH     project  controller  inspector
    |  1.   |      app manager |           |
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
    |    --admin maintenance actions--     |
    +--------------------------------------+
    |  10.  |         |        |           |
    +------------------------->+           |
    +<-------------------------+           |
    |       |         |        |    11.    |
    +------------------------------------->+
    |  12.  |         |        |           |
    +------>+   13.   |        |           |
    |       +-------->+        |           |
    +-------+---------+--------+-----------+

Concepts for maintenance type used below:

- `full maintenance`: This means maintenance will take a longer time and resource
  should be emptied, meaning container or VM need to be moved or deleted. Admin
  might need to test resource to work after maintenance.

- `reboot`: Only a reboot is needed and admin is do not need separate testing
  after that. Container or VM can be left in place if so wanted.

1.  Admin disables nova-compute to do planned maintenance on compute host and
    gets ACK from the API call. This is regardless the whole compute is affected
    by maintenance to make sure nothing is placed on part need to be maintained. 
2.  Admin tool sends project specific `planned maintenance` notification with
    detailed information about when maintenance is going to start, is it `reboot`
    or `full maintenance` including the information about project containers or
    VMs running on host or the part of it that will need maintenance.
3.  Application manager of the project receives AODH alarm about the same.
4.  Application manager can to switch over his ACT-STBY service, delete and
    re-instantiate his service on not affected resource if so wanted.
5.  Application manager call admin tool API to ACK to maintenance. Same time he
    gives instruction to migrate or leave remaining payload on host. Payload can
    be left on host if type of maintenance is just `reboot`.
6.  Admin tool does possible migration and receives an ACK.
7.  Admin tool send `in maintenance` notification that can be consumed by
    Inspector and other cloud services to know there is ongoing maintenance and
    things like automatic fault management actions for the host should be
    disabled.
8.  Admin tool sends project specific `in maintenance` notification if project
    has container or VM still running on host. In case of full maintenance where
    not all containers or VMs were not possible to be moved a `maintenance
    canceled` will be sent.
9.  Application manager of the project receives AODH alarm about the same.
10. Admin enables nova-compute service when maintenance is over and host can be
    put back to production. An ACK is received from API call.
11. Admin tool send `maintenance over` notification for Inspector and other cloud
    services.
12. Admin tool sends project specific `maintenance over` notification if project
    had container or VM still on host.
13. Application manager of the project receives AODH alarm about the same.

When admin tool sets planned maintenance, a uniq ID will be carried in all
places to identify the maintenance session. This uniq ID can be used by admin
or project to query the ongoing maintenance with admin tool API. Admin and
project specific views will be different as project will not be allowed to see
physical resources and surely not other projects.

POC
------------------

There was a `Maintenance POC`_ for planned maintenance in the OPNFV Beijing
summit to show the basic concept of using framework defined by the project.

.. _DOCTOR-52: https://jira.opnfv.org/browse/DOCTOR-52
.. _OPNFV Doctor project: https://wiki.opnfv.org/doctor
.. _use cases: http://artifacts.opnfv.org/doctor/docs/requirements/02-use_cases.html#nvfi-maintenance
.. _architecture: http://artifacts.opnfv.org/doctor/docs/requirements/03-architecture.html#nfvi-maintenance
.. _implementation:  http://artifacts.opnfv.org/doctor/docs/requirements/05-implementation.html#nfvi-maintenance
.. _planned maintenance session: https://lists.opnfv.org/pipermail/opnfv-tech-discuss/2017-June/016677.html
.. _Maintenance POC: https://wiki.opnfv.org/download/attachments/5046291/Doctor%20Maintenance%20PoC%202017.pptx?version=1&modificationDate=1498182869000&api=v2
