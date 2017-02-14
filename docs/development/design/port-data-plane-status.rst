.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

====================================
Port data plane status
====================================

https://bugs.launchpad.net/neutron/+bug/1598081

Neutron does not detect data plane failures affecting its logical resources.
This spec addresses that issue by means of allowing external tools to report to
Neutron about faults in the data plane that are affecting the ports. A new REST
API field is proposed to that end.


Problem Description
===================

An initial description of the problem was introduced in bug #159801 [1_]. This
spec focuses on capturing one (main) part of the problem there described, i.e.
extending Neutron's REST API to cover the scenario of allowing external tools
to report network failures to Neutron. Out of scope of this spec are works to
enable port status changes to be received and managed by mechanism drivers.

This spec also tries to address bug #1575146 [2_]. Specifically, and argued by
the Neutron driver team in [3_]:

 * Neutron should not shut down the port completly upon detection of physnet
   failure; connectivity between instances on the same node may still be
   reachable. Externals tools may or may not want to trigger a status change on
   the port based on their own logic and orchestration.

 * Port down is not detected when an uplink of a switch is down;

 * The physnet bridge may have multiple physical interfaces plugged; shutting
   down the logical port may not be needed in case network redundancy is in
   place.


Proposed Change
===============

A couple of possible approaches were proposed in [1_] (comment #3). This spec
proposes tackling the problema via a new extension API to the port resource.
The extension adds a new attribute 'dp-down' (data plane down) to represent the
status of the data plane. The field should be read-only by tenants and
read-write by admins.

Neutron should send out an event to the message bus upon toggling the data
plane status value. The event is relevant for e.g. auditing.


Data Model Impact
-----------------

A new attribute as extension will be added to the 'ports' table.

+------------+-------+----------+---------+--------------------+--------------+
|Attribute   |Type   |Access    |Default  |Validation/         |Description   |
|Name        |       |          |Value    |Conversion          |              |
+============+=======+==========+=========+====================+==============+
|dp_down     |boolean|RO, tenant|False    |True/False          |              |
|            |       |RW, admin |         |                    |              |
+------------+-------+----------+---------+--------------------+--------------+


REST API Impact
---------------

A new API extension to the ports resource is going to be introduced.

.. code-block:: python

  EXTENDED_ATTRIBUTES_2_0 = {
      'ports': {
          'dp_down': {'allow_post': False, 'allow_put': True,
                      'default': False, 'convert_to': convert_to_boolean,
                      'is_visible': True},
      },
  }


Examples
~~~~~~~~

Updating port data plane status to down:

.. code-block:: json

   PUT /v2.0/ports/<port-uuid>
   Accept: application/json
   {
       "port": {
           "dp_down": true
       }
   }



Command Line Client Impact
--------------------------

::

  neutron port-update [--dp-down <True/False>] <port>
  openstack port set [--dp-down <True/False>] <port>

Argument --dp-down is optional. Defaults to False.


Security Impact
---------------

None

Notifications Impact
--------------------

A notification (event) upon toggling the data plane status (i.e. 'dp-down'
attribute) value should be sent to the message bus. Such events do not happen
with high frequency and thus no negative impact on the notification bus is
expected.

Performance Impact
------------------

None

IPv6 Impact
-----------

None

Other Deployer Impact
---------------------

None

Developer Impact
----------------

None

Implementation
==============

Assignee(s)
-----------

 * cgoncalves

Work Items
----------

 * New 'dp-down' attribute in 'ports' database table
 * API extension to introduce new field to port
 * Client changes to allow for data plane status (i.e. 'dp-down' attribute')
   being set
 * Policy (tenants read-only; admins read-write)


Documentation Impact
====================

Documentation for both administrators and end users will have to be
contemplated. Administrators will need to know how to set/unset the data plane
status field.


References
==========

.. [1] RFE: Port status update,
   https://bugs.launchpad.net/neutron/+bug/1598081

.. [2] RFE: ovs port status should the same as physnet
   https://bugs.launchpad.net/neutron/+bug/1575146

.. [3] Neutron Drivers meeting, July 21, 2016
   http://eavesdrop.openstack.org/meetings/neutron_drivers/2016/neutron_drivers.2016-07-21-22.00.html
