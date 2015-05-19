====================================================
Report host fault to update server state immediately
====================================================

https://blueprints.launchpad.net/nova/+spec/update-server-state-immediately

A new API is needed to report a host fault to change the state of the
instances and compute node immediately. This allows usage of evacuate API
without a delay. The new API provides the possibility for external monitoring
system to detect any kind of host failure fast and reliably and inform
OpenStack about it. Nova updates the compute node state and states of the
instances. This way the states in the Nova DB will be in sync with the
real state of the system.

Problem description
===================
* Nova state change for failed or unreachable host is slow and does not
  reliably state compute node is down or not. This might cause same instance
  to run twice if action taken to evacuate instance to another host.
* Nova state for instances on failed compute node will not change,
  but remains active and running. This gives user a false information about
  instance state. Currently one would need to call "nova reset-state" for each
  instance to have them in error state.
* OpenStack user cannot make HA actions fast and reliably by trusting instance
  state and compute node state.
* As compute node state changes slowly one cannot evacuate instances.

Use Cases
---------
Use case in general is that in case there is a host fault one should change
compute node state fast and reliably when using DB servicegroup backend.
On top of this here is the use cases that are not covered currently to have
instance states changed correctly:
* Management network connectivity lost between controller and compute node.
* Host HW failed.

Generic use case flow:

* The external monitoring system detects a host fault.
* The external monitoring system fences the host if not down already.
* The external system calls the new Nova API to force the failed compute node
  into down state as well as instances running on it.
* Nova updates the compute node state and state of the effected instances to
  Nova DB.

Currently nova-compute state will be changing "down", but it takes a long
time. Server state keeps as "vm_state: active" and "power_state:
running", which is not correct. By having external tool to detect host faults
fast, fence host by powering down and then report host down to OpenStack, all
these states would reflect to actual situation. Also if OpenStack will not
implement automatic actions for fault correlation, external tool can do that.
This could be configured for example in server instance METADATA easily and be
read by external tool.

Project Priority
-----------------
Liberty priorities have not yet been defined.

Proposed change
===============
There needs to be a new API for Admin to state host is down. This API is used
to mark compute node and instances running on it down to reflect the real
situation.

Example on compute node is:

* When compute node is up and running:
  vm_state: active and power_state: running
  nova-compute state: up status: enabled
* When compute node goes down and new API is called to state host is down:
  vm_state: stopped power_state: shutdown
  nova-compute state: down status: enabled

vm_state values: soft-delete, deleted, resized and error
should not be touched.
task_state effect needs to be worked out if needs to be touched.

Alternatives
------------
There is no attractive alternatives to detect all different host faults than
to have a external tool to detect different host faults. For this kind of tool
to exist there needs to be new API in Nova to report fault. Currently there
must have been some kind of workarounds implemented as cannot trust or get the
states from OpenStack fast enough.

Data model impact
-----------------
None

REST API impact
---------------
* Update CLI to report host is down

  nova host-update command

  usage: nova host-update [--status <enable|disable>]
                        [--maintenance <enable|disable>]
                        [--report-host-down]
                        <hostname>

  Update host settings.

  Positional arguments

  <hostname>
  Name of host.

  Optional arguments

  --status <enable|disable>
  Either enable or disable a host.

  --maintenance <enable|disable>
  Either put or resume host to/from maintenance.

  --down
  Report host down to update instance and compute node state in db.

* Update Compute API to report host is down:

  /v2.1/{tenant_id}/os-hosts/{host_name}

  Normal response codes: 200
  Request parameters

  Parameter     Style   Type          Description
  host_name     URI     xsd:string    The name of the host of interest to you.

  {
      "host": {
          "status": "enable",
          "maintenance_mode": "enable"
          "host_down_reported": "true"

      }

  }

  {
      "host": {
          "host": "65c5d5b7e3bd44308e67fc50f362aee6",
          "maintenance_mode": "enabled",
          "status": "enabled"
          "host_down_reported": "true"

      }

  }

* New method to nova.compute.api module HostAPI class to have a
  to mark host related instances and compute node down:
  set_host_down(context, host_name)

* class novaclient.v2.hosts.HostManager(api) method update(host, values)
  Needs to handle reporting host down.

* Schema does not need changes as in db only service and server states are to
  be changed.

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
Only impact is that user can get information faster about instance and
compute node state. This also gives possibility to evacuate faster.
No impact that would slow down. Host down should be rare occurrence.

Other deployer impact
---------------------
Developer can make use of any external tool to detect host fault and report it
to OpenStack.

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
Test cases that exists for enabling or putting host to maintenance should be
altered or similar new cases made test new functionality.

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
* High Availability guide might have page to tell external tool could provide
  ability to provide faster HA as able to update states by new API.
  http://docs.openstack.org/high-availability-guide/content/index.html

References
==========
* OPNFV Doctor project: https://wiki.opnfv.org/doctor
* OpenStack Instance HA Proposal:
  http://blog.russellbryant.net/2014/10/15/openstack-instance-ha-proposal/
* The Different Facets of OpenStack HA:
  http://blog.russellbryant.net/2015/03/10/
  the-different-facets-of-openstack-ha/
