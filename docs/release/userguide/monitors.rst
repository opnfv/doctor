.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Monitor Types and Limitations
=============================

Currently there are two monitor types supported: sample and collectd

Sample Monitor
--------------

Sample monitor type pings the compute host from the control host and calculates the
notification time after the ping timeout.
Also if inspector type is sample, the compute node needs to communicate with the control
node on port 12345. This port needs to be opened for incomming traffic on control node.

Collectd Monitor
----------------

Collectd monitor type uses collectd daemon running ovs_events plugin. Collectd runs on
compute to send instant notification to the control node. The notification time is
calculated by using the difference of time at which compute node sends notification to
control node and the time at which consumer is notified. The time on control and compute
node has to be synchronized for this reason. For further details on setting up collectd
on the compute node, use the following link:
:doc:`<barometer:release/userguide/feature.userguide>`


Collectd monitors an interface managed by OVS. If the interface is not be assigned
an IP, the user has to provide the name of interface to be monitored. The command to
launch the doctor test in that case is:
MONITOR_TYPE=collectd INSPECTOR_TYPE=sample INTERFACE_NAME=example_iface ./run.sh

If the interface name or IP is not provided, the collectd monitor type will monitor the
default management interface. This may result in the failure of doctor run.sh test case.
The test case sets the monitored interface down and if the inspector (sample or congress)
is running on the same subnet, collectd monitor will not be able to communicate with it.
