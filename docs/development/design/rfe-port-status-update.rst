.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

==========================
Neutron Port Status Update
==========================

.. NOTE::
   This document represents a Neutron RFE reviewed in the Doctor project before submitting upstream to Launchpad Neutron
   space. The document is not intended to follow a blueprint format or to be an extensive document.
   For more information, please visit http://docs.openstack.org/developer/neutron/policies/blueprints.html

   The RFE was submitted to Neutron. You can follow the discussions in https://bugs.launchpad.net/neutron/+bug/1598081

Neutron port status field represents the current status of a port in the cloud infrastructure. The field can take one of
the following values: 'ACTIVE', 'DOWN', 'BUILD' and 'ERROR'.

At present, if a network event occurs in the data-plane (e.g. virtual or physical switch fails or one of its ports,
cable gets pulled unintentionally, infrastructure topology changes, etc.), connectivity to logical ports may be affected
and tenants' services interrupted. When tenants/cloud administrators are looking up their resources' status (e.g. Nova
instances and services running in them, network ports, etc.), they will wrongly see everything looks fine. The problem
is that Neutron will continue reporting port 'status' as 'ACTIVE'.

Many SDN Controllers managing network elements have the ability to detect and report network events to upper layers.
This allows SDN Controllers' users to be notified of changes and react accordingly. Such information could be consumed
by Neutron so that Neutron could update the 'status' field of those logical ports, and additionally generate a
notification message to the message bus.

However, Neutron misses a way to be able to receive such information through e.g. ML2 driver or the REST API ('status'
field is read-only). There are pros and cons on both of these approaches as well as other possible approaches. This RFE
intends to trigger a discussion on how Neutron could be improved to receive fault/change events from SDN Controllers or
even also from 3rd parties not in charge of controlling the network (e.g. monitoring systems, human admins).
