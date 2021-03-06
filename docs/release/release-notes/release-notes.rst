.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Iruya version of Doctor.

Important notes
===============

Jerma release has mainly been for finalizing maintenance use case testing
supporting the ETSI FEAT03 defined interactino between VNFM and infrastructure.
This is mainly to have infrastructure maintenance and upgrade operations
opttimized as fast as they can while keeping VNFs on top with zero impact
on their service.

Further more this is the final release of Doctor and the more deep testing is
moving more to upstream projects like Fenix for the maintenance. Also in
this release we have made sure that all Doctor testing and any deeper testing
with ehe upstream projects can be done in DevStack. This also makes DevStack
the most important installer.

Summary
=======

Jerma Doctor framework uses OpenStack Train integrated into its test cases.

Release Data
============

Doctor changes

- Maintenance use case updated to support latest version of Fenix.
- Maintenance use case now supports ETSI FEAT03 optimization with Fenix.
- Doctor testing is now preferred to be done in DevStack environment
  where one can easily select OpenStack release from Rocky to Ussuri to
  test Doctor functionality. Latest OPNFV Fuel can also be used for the
  OpenStack version it supports.

Doctor CI

- Doctor tested with fuel installer.
- Fault management use case is tested with sample inspector.
- Maintenance use case is tested with sample implementation and towards
  the latest Fenix version. The includes the new ETSI FEAT03 optimization.

Version change
^^^^^^^^^^^^^^

Module version changes
~~~~~~~~~~~~~~~~~~~~~~

- OpenStack has changed Train

Document version changes
~~~~~~~~~~~~~~~~~~~~~~~~

All documentation is updated to OPNFV unified format according to
documentation guidelines. Small updates in many documents. 

Reason for version
^^^^^^^^^^^^^^^^^^

N/A

Feature additions
~~~~~~~~~~~~~~~~~

+--------------------+--------------------------------------------+
| **JIRA REFERENCE** | **SLOGAN**                                 |
+--------------------+--------------------------------------------+
| DOCTOR-137         | VNFM maintenance with ETSI changes         |
+--------------------+--------------------------------------------+
| DOCTOR-136	     | DevStack support                           |
+--------------------+--------------------------------------------+


Deliverables
------------

Software deliverables
=====================

None

Documentation deliverables
==========================

https://git.opnfv.org/doctor/tree/docs

Known Limitations, Issues and Workarounds
=========================================

System Limitations
^^^^^^^^^^^^^^^^^^

Maintenance test case requirements:

- Minimum number of nodes:   1 Controller, 3 Computes
- Min number of VCPUs:       2 VCPUs for each compute

Known issues
^^^^^^^^^^^^

None

Workarounds
^^^^^^^^^^^

None

Test Result
===========

Doctor CI results with TEST_CASE='fault_management' and INSPECTOR_TYPE=sample
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='fuel'                | SUCCESS      |
+--------------------------------------+--------------+

Doctor CI results with TEST_CASE='maintenance' and INSPECTOR_TYPE=sample
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='fuel'                | SUCCESS      |
| ADMIN_TOOL_TYPE='fenix' *)           |              |
+--------------------------------------+--------------+

*) Sample implementation not updated according to latest upstream Fenix
   and is currently not being tested.

References
==========

For more information about the OPNFV Doctor latest work, please see:

https://wiki.opnfv.org/display/doctor/Doctor+Home

Further information about ETSI FEAT03 optimization can be found from Fenix
Documentation:

https://fenix.readthedocs.io/en/latest
