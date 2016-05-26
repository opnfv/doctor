.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Annex: NFVI Faults
=================================================

Faults in the listed elements need to be immediately notified to the Consumer in
order to perform an immediate action like live migration or switch to a hot
standby entity. In addition, the Administrator of the host should trigger a
maintenance action to, e.g., reboot the server or replace a defective hardware
element.

Faults can be of different severity, i.e., critical, warning, or
info. Critical faults require immediate action as a severe degradation of the
system has happened or is expected. Warnings indicate that the system
performance is going down: related actions include closer (e.g. more frequent)
monitoring of that part of the system or preparation for a cold migration to a
backup VM. Info messages do not require any action. We also consider a type
"maintenance", which is no real fault, but may trigger maintenance actions
like a re-boot of the server or replacement of a faulty, but redundant HW.

Faults can be gathered by, e.g., enabling SNMP and installing some open source
tools to catch and poll SNMP. When using for example Zabbix one can also put an
agent running on the hosts to catch any other fault. In any case of failure, the
Administrator should be notified. The following tables provide a list of high
level faults that are considered within the scope of the Doctor project
requiring immediate action by the Consumer.

**Compute/Storage**

+-------------------+----------+------------+-----------------+----------------+
| Fault             | Severity | How to     | Comment         | Action to      |
|                   |          | detect?    |                 | recover        |
+===================+==========+============+=================+================+
| Processor/CPU     | Critical | Zabbix     |                 | Switch to      |
| failure, CPU      |          |            |                 | hot standby    |
| condition not ok  |          |            |                 |                |
+-------------------+----------+------------+-----------------+----------------+
| Memory failure/   | Critical | Zabbix     |                 | Switch to      |
| Memory condition  |          | (IPMI)     |                 | hot standby    |
| not ok            |          |            |                 |                |
+-------------------+----------+------------+-----------------+----------------+
| Network card      | Critical | Zabbix/    |                 | Switch to      |
| failure, e.g.     |          | Ceilometer |                 | hot standby    |
| network adapter   |          |            |                 |                |
| connectivity lost |          |            |                 |                |
+-------------------+----------+------------+-----------------+----------------+
| Disk crash        | Info     | RAID       | Network storage | Inform OAM     |
|                   |          | monitoring | is very         |                |
|                   |          |            | redundant (e.g. |                |
|                   |          |            | RAID system)    |                |
|                   |          |            | and can         |                |
|                   |          |            | guarantee high  |                |
|                   |          |            | availability    |                |
+-------------------+----------+------------+-----------------+----------------+
| Storage           | Critical | Zabbix     |                 | Live migration |
| controller        |          | (IPMI)     |                 | if storage     |
|                   |          |            |                 | is still       |
|                   |          |            |                 | accessible;    |
|                   |          |            |                 | otherwise hot  |
|                   |          |            |                 | standby        |
+-------------------+----------+------------+-----------------+----------------+
| PDU/power         | Critical | Zabbix/    |                 | Switch to      |
| failure, power    |          | Ceilometer |                 | hot standby    |
| off, server reset |          |            |                 |                |
+-------------------+----------+------------+-----------------+----------------+
| Power             | Warning  | SNMP       |                 | Live migration |
| degration, power  |          |            |                 |                |
| redundancy lost,  |          |            |                 |                |
| power threshold   |          |            |                 |                |
| exceeded          |          |            |                 |                |
+-------------------+----------+------------+-----------------+----------------+
| Chassis problem   | Warning  | SNMP       |                 | Live migration |
| (e.g. fan         |          |            |                 |                |
| degraded/failed,  |          |            |                 |                |
| chassis power     |          |            |                 |                |
| degraded), CPU    |          |            |                 |                |
| fan problem,      |          |            |                 |                |
| temperature/      |          |            |                 |                |
| thermal condition |          |            |                 |                |
| not ok            |          |            |                 |                |
+-------------------+----------+------------+-----------------+----------------+
| Mainboard failure | Critical | Zabbix     | e.g. PCIe, SAS  | Switch to      |
|                   |          | (IPMI)     | link failure    | hot standby    |
+-------------------+----------+------------+-----------------+----------------+
| OS crash (e.g.    | Critical | Zabbix     |                 | Switch to      |
| kernel panic)     |          |            |                 | hot standby    |
+-------------------+----------+------------+-----------------+----------------+

**Hypervisor**

+----------------+----------+------------+-------------+-------------------+
| Fault          | Severity | How to     | Comment     | Action to         |
|                |          | detect?    |             | recover           |
+================+==========+============+=============+===================+
| System has     | Critical | Zabbix     |             | Switch to         |
| restarted      |          |            |             | hot standby       |
+----------------+----------+------------+-------------+-------------------+
| Hypervisor     | Warning/ | Zabbix/    |             | Evacuation/switch |
| failure        | Critical | Ceilometer |             | to hot standby    |
+----------------+----------+------------+-------------+-------------------+
| Hypervisor     | Warning  | Alarming   | Zabbix/     | Live migration    |
| status not     |          | service    | Ceilometer  |                   |
| retrievable    |          |            | unreachable |                   |
+----------------+----------+------------+-------------+-------------------+

**Network**

+------------------+----------+---------+----------------+---------------------+
| Fault            | Severity | How to  | Comment        | Action to           |
|                  |          | detect? |                | recover             |
+==================+==========+=========+================+=====================+
| SDN/OpenFlow     | Critical | Ceilo-  |                | Switch to           |
| switch,          |          | meter   |                | hot standby         |
| controller       |          |         |                | or reconfigure      |
| degraded/failed  |          |         |                | virtual network     |
|                  |          |         |                | topology            |
+------------------+----------+---------+----------------+---------------------+
| Hardware failure | Warning  | SNMP    | Redundancy of  | Live migration if   |
| of physical      |          |         | physical       | possible otherwise  |
| switch/router    |          |         | infrastructure | evacuation          |
|                  |          |         | is reduced or  |                     |
|                  |          |         | no longer      |                     |
|                  |          |         | available      |                     |
+------------------+----------+---------+----------------+---------------------+
