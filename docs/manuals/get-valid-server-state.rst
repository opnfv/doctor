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

Previously when the owner of a VM has queried his VMs, he has not gotten
enough state information, states have not changed fast enough and they have
not been accurate in some scenarios. With this change this gap is now
fullfilled.

A typical case is that user with high available application needs to make
immediate switchover for service in case of a fault. Now if compute host is
forced down as result of a fault, user needs to get this state information and
act accordingly. Also maintenance has not been shown to user while also
needed.

What is changed
===============

A new ``host_status`` parameter is added to the ``/servers/{server_id}`` and
``/servers/detail`` endpoints in microversion 2.16. By this new parameter
user can get more state information about the host that is needed when other
existing state information about VM state is not enough.

``host_status`` possible values where next value in list can override the
previous::

  UP if nova-compute up.
  UNKNOWN if nova-compute not reported by servicegroup driver.
  DOWN if nova-compute forced down.
  MAINTENANCE if nova-compute is disabled.
  Empty string indicates there is no host for server.

``host_status`` appears in the response only if the policy permits. By
default the policy is for admin only in Nova policy.json::

  "os_compute_api:servers:show:host_status": "rule:admin_api"

in NFV use this has to be enabled also for owner of VM::

  "os_compute_api:servers:show:host_status": "rule:admin_or_owner"

REST API examples:
==================

Case where nova-compute enabled and reporting normally::

    GET /v2.1/{tenant_id}/servers/{server_id}

    200 OK
    {
      "server": {
        "host_status": "UP",
        ...
      }
    }

Case where nova-compute enabled, but not reporting normally::

    GET /v2.1/{tenant_id}/servers/{server_id}

    200 OK
    {
      "server": {
        "host_status": "UNKNOWN",
        ...
      }
    }

Case where nova-compute enabled, but forced_down::

    GET /v2.1/{tenant_id}/servers/{server_id}

    200 OK
    {
      "server": {
        "host_status": "DOWN",
        ...
      }
    }

Case where nova-compute disabled::

    GET /v2.1/{tenant_id}/servers/{server_id}

    200 OK
    {
      "server": {
        "host_status": "MAINTENANCE",
        ...
      }
    }

This is also seenin  python-novaclient as::

  +-------+------+--------+------------+-------------+----------+-------------+
  | ID    | Name | Status | Task State | Power State | Networks | Host Status |
  +-------+------+--------+------------+-------------+----------+-------------+
  | 9a... | vm1  | ACTIVE | -          | RUNNING     | xnet=... | UP          |
  +-------+------+--------+------------+-------------+----------+-------------+

Links:
======

OpenStack compute manual page:
http://developer.openstack.org/api-ref-compute-v2.1.html#compute-v2.1
