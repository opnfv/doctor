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

Compute
-------
- CPU
  - detect: Zabbix
  - fault
    - fail: critical
  - action: switch to hot standby
- RAM
  - detect: Zabbix
  - fault
    - fail: critical
  - action: switch to hot standby
- NIC
  - detect: Zabbix / Ceilometer
  - fault
    - fail: critical
    - connection lost: critical
  - action: switch to hot standby
- PCIe
  - detect: SNMP
  - fault
    - fail: Critical
  - action: switch to hot standby
- hard drive
  - detect: RAID monitoring / S.M.A.R.T / Zabbix
  - fault
    - crash: info
    - aging: info
    - controller fail: critical
  - action: inform OAM
- Power
  - detect: SNMP
  - fault
    - off: critical
    - degraded: warning
    - redundancy lost: warning
    - threshold exceeded: warning
  - action: switch to hot standby

Storage
-------
- controller
  - detect: SNMP
  - fault
    - fail: critical
  - action: switch to hot standby
- temperature
  - detect: SNMP
  - fault
    - too high: warning
  - action: live migration
- fan
  - detect: SNMP
  - fault
    - fail: warning
  - action: live migration
- SAS link
  - detect: SNMP
  - fault
    - fail: critical
  - action: switch to hot standby
- NIC
  - detect :SNMP
  - fault
    - fail: warning
  - action: live migration

Network
-------
- external switch interface
  - detect: SNMP
  - fault
    - fail: critical
    - degraded: warning
  - action: live migration
- SDN/OpenFlow switch
  - detect: ?
  - fault
    - fail: critical
    - degraded: warning
  - action: live migration
- Physical switch
  - detect: SNMP
  - fault
    - fail: warning
  - action: live migration
- Physical router
  - detect: SNMP
  - fault
    - fail: warning
  - action: live migration

Chassis
-------
- fan
  - detect: SNMP
  - fault
    - degraded: warning
  - action: live migration
- power supply
  - detect: SNMP
  - fault
    - input error: critical
    - redundant lost: warning
  - action: live migration

Hypervisor
----------
- system
  - detect: Zabbix
  - fault
    - restarted
  - action: switch to hot standby
- hypervisor
  - detect: Zabbix / Ceilometer
  - fault
    - failure: critical
  - action: switch to hot standby

Monitor
-------
- Zabbix/Ceilometer
  - detect: ?
  - fault
    - unreachable: warning
  - action: live migration
