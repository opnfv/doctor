..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Set maintenance period
==========================================

https://blueprints.launchpad.net/nova/+spec/set-maintenance-period

When compute host going for maintenance it has to be possible to set the wanted
maintenance start and end time.

Problem description
===================

Admin needs to be able to set wanted maintenance period, so server owner can
also prepare for maintenance. Server owner might want to have different actions
for his server depending when and how long the maintenance takes. This is very
important for services that needs to run without any downtime because of the
maintenance.

Use Cases
---------

As admin I want to set maintenance period for certain host.

As owner of a server I want to prepare for maintenance to minimize downtime and
keep capacity on needed level.

As owner of a server I want to have different actions for different servers
depending aplication on server, when and how long the maintenance will last. To
achieve this, there needs to be information about when maintenance in going to
happen. Actions for servers are not in scope of this spec. It might be future
work to define some auto recovery or some other configured actions, but
currently that is just left outside of Nova scope. This can be complex and it
might be server is moved, removed or even left to host when maintenance is to
take place.

Proposed change
===============

New admin API endpoint PUT /v2.1/{tenant_id}/os-services/maintenance should be
added having ``host``, ``binary``, ``maintenance_start`` and
``maintenance_end`` parameters in request. API will tell when actual
maintenance for host will happen and it is also used to unset maintenance
period. As in disable nova-compute case only the scheduling will be stopped,
this new API will tell the time period when actually host maintenance is
performed and servers can also therefore be down.

If no ``maintenance_end`` defined while ``maintenance_start`` defined, it means
the host will be removed. Calling API with empty timestamps in
``maintenance_start`` and ``maintenance_end`` will indicate there is no
ongoing maintenance and this is also the default value in Nova service DB for
these new fields. Service enable/disable is expected to be called separately
before and after maintenance.

``service.update`` notification should have new version to include
``maintenance_start`` and maintenance_end`` information. Calling of new
maintenance API should also trigger this notification.

Alarm should be risen for server owners telling list of their servers that are
on a host that is going for maintenance. Also the `maintenance_start`` and
``maintenance_end`` should be visible in the alarm. Host should not be exposed
to owner, so alarm should not contain that information. There should also be
alarm when maintenance over and it needs to contain information to map it to
start maintenance alarm. tbd better in the notification section.

Maintenance should also be shown to server owner by adding
``OS-EXT-SRV-ATTR:maintenance_start`` and ``OS-EXT-SRV-ATTR:maintenance_end``
parameters to the ``/servers/{server_id}`` and ``/servers/detail`` endpoints.
New policy should be added to control visibility of the new parameters:

"os_compute_api:servers:show:maintenance": "rule:admin_or_owner"

Currently only ability to show nova-compute service disabled as ``MAINTENANCE``
in ``host_status`` parameter, but policy for this defaults to admin. In NFV it
will be configured also to owner.

Alternatives
------------

tbd

Data model impact
-----------------

Nova Service DB will have new fields ``maintenance_start`` and
``maintenance_end``.

REST API impact
---------------

New API microversion is needed to add new API:
PUT /v2.1/{tenant_id}/os-services/maintenance
Same time also visibility to response of
GET ``/v2.1/\u200b{tenant_id}/servers/{server_id}`` and
GET ``/v2.1/\u200b{tenant_id}/servers/detail`` with new parameters
``OS-EXT-SRV-ATTR:maintenance_start`` and ``OS-EXT-SRV-ATTR:maintenance_end``.
Parameters visibility controlled by new policy.

Example of setting 2 hours maintenance period::

    PUT /v2.1/{tenant_id}/os-services/maintenance
    {
        "host": "compute1",
        "binary": "nova-compute",
        "maintenance_start": "2016-03-22T01:00:00",
        "maintenance_end": "2016-03-22T03:00:00"
    }

    200 OK
    {
        "service": {
            "binary": "nova-compute",
            "host": "compute1",
            "maintenance_start": "2016-03-22T01:00:00.000000",
            "maintenance_end": "2016-03-22T03:00:00.000000"
        }
    }

Example to unset maintenance::

    PUT /v2.1/{tenant_id}/os-services/maintenance
    {
        "host": "compute1",
        "binary": "nova-compute",
        "maintenance_start": "",
        "maintenance_end": ""
    }

    200 OK
    {
        "service": {
            "binary": "nova-compute",
            "host": "compute1",
            "maintenance_start": "",
            "maintenance_end": ""
        }
    }

Example of indicating host removal::

    PUT /v2.1/{tenant_id}/os-services/maintenance
    {
        "host": "compute1",
        "binary": "nova-compute",
        "maintenance_start": "2016-03-22T01:00:00",
        "maintenance_end": ""
    }

    200 OK
    {
        "service": {
            "binary": "nova-compute",
            "host": "compute1",
            "maintenance_start": "2016-03-22T01:00:00.000000",
            "maintenance_end": ""
        }
    }

Setting timestamps in the past will be considered as an error and
``maintenance_end`` has to be after ``maintenance_start`` or empty::

    400 Bad Request

Security impact
---------------

None

Notifications impact
--------------------

New version of service.update notification needs to have new parameters
``maintenance_start`` and ``maintenance_end`` and notification needs to be
triggered if new maintenance API is called::

    {
        "priority":"INFO",
        "event_type":"service.update",
        "timestamp":"2016-03-22 00:46:25.211575",
        "publisher_id":"nova-compute:controller",
        "payload":{
            "nova_object.version":"1.0",
            "nova_object.name":"ServiceStatusPayload",
            "nova_object.namespace":"nova",
            "nova_object.data":{
                "binary":"nova-compute",
                "report_count":1,
                "topic":"compute",
                "host":"controller",
                "version":3,
                "disabled":true,
                "forced_down":false,
                "last_seen_up":"2016-03-22T00:46:25Z",
                "disabled_reason":"Going to maintenance",
                "maintenance_start": "2016-03-22T01:00:00Z",
                "maintenance_end": "2016-03-22T03:00:00Z",
            }
        },
        "message_id":"8516b5c7-c6a7-43a4-9ad1-df447f318afb"
    }

tbd, maintenance alarm.

Other end user impact
---------------------

None

Performance Impact
------------------

None

Other deployer impact
---------------------

None

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  tomi-juvonen-q

Work Items
----------

Nova service DB changes.
New maintenance API.
Notification.
Alarm.

Dependencies
============

Continues work started in Mitaka:

https://blueprints.launchpad.net/nova/+spec/get-valid-server-state

Testing
=======

Unit and functional tests will be added.

Documentation Impact
====================

API changes need to be documented for new microversion.
Maintenance documentation should be updated.

References
==========

Requirements of OPNFV Doctor project:
http://artifacts.opnfv.org/doctor/docs/requirements/requirements.pdf

History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Newton
     - Introduced
