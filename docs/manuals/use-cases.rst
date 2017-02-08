.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

=========
Use Cases
=========

In this section, you can find some NFV use cases, and understand how they can
be addressed by the Doctor framework. The use cases will describe different
examples of fault correlations:

* Between a physical resource and another physical resource
* Between a physical resource and a virtual resource
* Between a virtual resource and another virtual resource

Physical Switch Failure
=======================

This use case demonstrates fault correlation between two physical resources:
a switch and a host. It also demonstrates the effect that this failure has on
the virtual resources (instances).

A failure on a physical switch results in the attached host becoming
unreachable. All instances running on this host will also become unreachable,
and the applications using these instances will either fail or will no longer
be highly available. In the world of NFV, it is critical to identify this fault
as fast as possible and take corrective actions. By the time the VNFM notices
the problem in the application it might be too late.

The Doctor architecture handles this use case by providing a fast alarm
propagation from the switch to the host and to the instances running on it.

* The Monitor detects a fault in the physical switch, and sends an event to the Inspector.
* The Inspector identifies the affected resources (in that case, the host) based on the resource topology.
* The Inspector notifies the Controller (in that case, Nova) that the host is down.
* The Controller sends a notification to the Notifier.
* Optionally, the Inspector notifies the Notifier directly about all the affected resources (host and instances).
* The Notifier notifies the Consumer/VNFM, which can take corrective actions like perform a switchover or evacuate the failed host.

The result of using the Doctor framework is that the Consumer/VNFM could
prevent the end user from being affected by the fault, e.g., by performing
a switchover from the active instance to the standby one in less than
one second.


Physical Port Failure – HA Use Case
===================================

This use case demonstrates fault correlation between a physical resource
(a port) to a virtual resource (a bridge) and to other virtual resources
(instances). It also demonstrates how the Doctor framework can be used to
support HA scenarios and to avoid a single point of failure, in case one of
two ports fails.

It is similar to the Physical Switch Failure, but a bit more complex.
Here, the network type is used to determine the relationship between
an instance and the bridges it is using. A failure in a physical port will
affect some of the instances, but not all of them.

A short description of the topology: a bridge has a bond of two physical ports.
Several bridges may be connected to one another, and the traffic that goes
through them depends on the network type of each instance (vlan, vxlan, etc.).
In case of a physical port failure, the Inspector should warn that instances
using this bridge are at risk of becoming unreachable. In case both ports of
the bridge failed, it is a critical error.

This would be the flow:

* The Monitor detects a fault in the physical port, and sends an event to the Inspector.
* The Inspector identifies the affected resources (in that case, the bridge and the instances that are using it for their network traffic) based on the resource topology.
* The Inspector notifies the Notifier that these resources are at risk of becoming unreachable.
* The Notifier notifies the Consumer/VNFM, which can take preventive actions like perform a switchover to the standby instances.

The result of using the Doctor framework is that the Consumer/VNFM could be
proactive and prevent a failure that might happen, e.g., by doing a switchover
from the active instance to the standby one as a precaution.
