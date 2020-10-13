.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

======================
Get valid server state
======================

Related Blueprints:
===================

https://blueprints.launchpad.net/nova/+spec/get-valid-server-state

Problem description
===================

Previously when the owner of a VM has queried his VMs, he has not received
enough state information, states have not changed fast enough in the VIM and
they have not been accurate in some scenarios. With this change this gap is now
closed.

A typical case is that, in case of a fault of a host, the user of a high
availability service running on top of that host, needs to make an immediate
switch over from the faulty host to an active standby host. Now, if the compute
host is forced down [1] as a result of that fault, the user has to be notified
about this state change such that the user can react accordingly. Similarly,
a change of the host state to "maintenance" should also be notified to the
users.

What is changed
===============

A new ``host_status`` parameter is added to the ``/servers/{server_id}`` and
``/servers/detail`` endpoints in microversion 2.16. By this new parameter
user can get additional state information about the host.

``host_status`` possible values where next value in list can override the
previous:

- ``UP`` if nova-compute is up.
- ``UNKNOWN`` if nova-compute status was not reported by servicegroup driver
  within configured time period. Default is within 60 seconds,
  but can be changed with ``service_down_time`` in nova.conf.
- ``DOWN`` if nova-compute was forced down.
- ``MAINTENANCE`` if nova-compute was disabled. MAINTENANCE in API directly
  means nova-compute service is disabled. Different wording is used to avoid
  the impression that the whole host is down, as only scheduling of new VMs
  is disabled.
- Empty string indicates there is no host for server.

``host_status`` is returned in the response in case the policy permits. By
default the policy is for admin only in Nova policy.json::

  "os_compute_api:servers:show:host_status": "rule:admin_api"

For an NFV use case this has to also be enabled for the owner of the VM::

  "os_compute_api:servers:show:host_status": "rule:admin_or_owner"

REST API examples:
==================

Case where nova-compute is enabled and reporting normally::

    GET /v2.1/{tenant_id}/servers/{server_id}

    200 OK
    {
      "server": {
        "host_status": "UP",
        ...
      }
    }

Case where nova-compute is enabled, but not reporting normally::

    GET /v2.1/{tenant_id}/servers/{server_id}

    200 OK
    {
      "server": {
        "host_status": "UNKNOWN",
        ...
      }
    }

Case where nova-compute is enabled, but forced_down::

    GET /v2.1/{tenant_id}/servers/{server_id}

    200 OK
    {
      "server": {
        "host_status": "DOWN",
        ...
      }
    }

Case where nova-compute is disabled::

    GET /v2.1/{tenant_id}/servers/{server_id}

    200 OK
    {
      "server": {
        "host_status": "MAINTENANCE",
        ...
      }
    }

Host Status is also visible in python-novaclient::

  +-------+------+--------+------------+-------------+----------+-------------+
  | ID    | Name | Status | Task State | Power State | Networks | Host Status |
  +-------+------+--------+------------+-------------+----------+-------------+
  | 9a... | vm1  | ACTIVE | -          | RUNNING     | xnet=... | UP          |
  +-------+------+--------+------------+-------------+----------+-------------+

Links:
======

[1] Manual for OpenStack NOVA API for marking host down
http://artifacts.opnfv.org/doctor/docs/manuals/mark-host-down_manual.html

[2] OpenStack compute manual page
http://developer.openstack.org/api-ref-compute-v2.1.html#compute-v2.1
