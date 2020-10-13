.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Iruya version of Doctor.

Important notes
===============

In Iruya release there has not been many changes.

All testing is now being made with Fuel installer. Maintenance use case
is now only tested against latest upstream Fenix. Only sample inspector is
tested as Fuel do not support Vitrage or Congress.

Summary
=======

Iruya Doctor framework uses OpenStack Stein integrated into its test cases.

Release Data
============

Doctor changes

- Maintenance use case updated to support latest version of Fenix running
  in container on controller node
- Maintenance use case now support Fuel installer
- Doctor updated to use OpenStack Stein and only python 3.6
- Testing only sample inspector as lacking installer support for
  Vitrage and Congress

Releng changes

- Doctor testing running with python 3.6 and with sample inspector
- Doctor is only tested with Fuel installer

Version change
^^^^^^^^^^^^^^

Module version changes
~~~~~~~~~~~~~~~~~~~~~~

- OpenStack has changed from Rocky to Stein since previous Hunter release.

Document version changes
~~~~~~~~~~~~~~~~~~~~~~~~

N/A

Reason for version
^^^^^^^^^^^^^^^^^^

N/A

Feature additions
~~~~~~~~~~~~~~~~~

+--------------------+--------------------------------------------------------------+
| **JIRA REFERENCE** | **SLOGAN**                                                   |
+--------------------+--------------------------------------------------------------+
| DOCTOR-134         | Update Doctor maintenance use case to work with latest Fenix |
+--------------------+--------------------------------------------------------------+

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
