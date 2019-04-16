.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Hunter of Doctor.

Important notes
===============

In Hunter release, Doctor has been working with fault management alarming
enhancement and maintenance use case to upstream.

OpenStack Fenix (unofficial project) has been futher worked to implement the
infrastructure rolling maintenance in interaction with VNFM. Doctor CI testing
also supports maintenance testing with Fenix latest master version.

MCP and Apex installers are currently supported. In MCP we test fault management
without the enhanced alarm. In Apex we test fault management with alarm
enhancement with sample implementation. Apex is also used for maintenance use
case testing. Congress inspector support is not working.

In this release, Doctor has not yet been working to look outside OpenStack.
We might need to get back to this later to better meet the tough industry
requirements as well as requirements from edge, containers and 5G.

Summary
=======

Hunter Doctor framework uses OpenStack Rocky integrated into its test cases.
For testing, we use Doctor CI on OPNFV installers.

Release Data
============

Doctor changes

+------------------------------------------+----------------------------------------------------------+
| **commit-ID**                            | **Subject**                                              |
+------------------------------------------+----------------------------------------------------------+
| b19b69d731cfb5a87f7c928cc898ea04ec85cec6 | Fix tox to clean python cache                            | 
+------------------------------------------+----------------------------------------------------------+
| 364d2c2344be5775a0eef6fe19fda125d2c8853d | Handle the exception for running the profiler            |
+------------------------------------------+----------------------------------------------------------+
| e6c857ba931a03fb7bfb49746cc4a7eb5b6ce6e1 | Hunter release documentation                             |
+------------------------------------------+----------------------------------------------------------+
| 73605c5c34b97ab56306bfa9af0f5888f3c7e46d | Support Fenix as admin tool                              |
+------------------------------------------+----------------------------------------------------------+
| 33293e9c23a21ad3228f46d2063f18c915eb2b79 | Wrong yamllint disable command                           |
+------------------------------------------+----------------------------------------------------------+
| d82ab34f15a9b67185c85c6afc5562bc8b72cb8b | Add local.conf.sample for devstack deployment of Doctor  |
+------------------------------------------+----------------------------------------------------------+
| 7ecc40b445b2aa42f0680c96dc672accf4e40ba0 | Hi, the automation job failed.                           |
+------------------------------------------+----------------------------------------------------------+
| 2cd1ca4463121e2354fd920af2b26c65848fb9e2 | Remove Ryota from committers                             |
+------------------------------------------+----------------------------------------------------------+
| f31ab961c594595772b0c3d4bd40a0d9491fc6cb | Removing committers                                      |
+------------------------------------------+----------------------------------------------------------+
| c653d95c67436698296e238396bf5d8370e3169a | Update to INFO file                                      |
+------------------------------------------+----------------------------------------------------------+
| e6708c869855ab69f9b53959befd82bb2f32f9ad | Bug - Testing in Apex with OpenStack master fails        |
+------------------------------------------+----------------------------------------------------------+
| e1c5dd0158d5168738fcc9918d24c04ca724b056 | remove to set ceilometer config in MCP                   |
+------------------------------------------+----------------------------------------------------------+
| d673e9218a53e047edc5ff6cd047ac6db5112651 | Support Fenix and sample implementation accordingly      |
+------------------------------------------+----------------------------------------------------------+
| 916e4931a56c1a5d41d46148609bf348d4326d37 | fix the configparser for  Python 2 and 3 Compatibility   |
+------------------------------------------+----------------------------------------------------------+
| 4075b417e973adb257ae39ff5c25aa182a2af3ea | index.rst was blank                                      |
+------------------------------------------+----------------------------------------------------------+
| dafdfcfad6866d7c413d4b8d5a9d25f3ab1f76dc | Minor docs updates                                       |
+------------------------------------------+----------------------------------------------------------+

Releng changes

+------------------------------------------+----------------------------------------------------------+
| **commit-ID**                            | **Subject**                                              |
+------------------------------------------+----------------------------------------------------------+
| cc290b2f937a2edbd60a5d2d1e20f333dfc7eb88 | Doctor to run Fenix as admin tool                        |
+------------------------------------------+----------------------------------------------------------+
| 488c558492201aacd359305a7afa3d5640a90b0e | Add parameter of `DEPLOY_SCENARIO` for doctor            |
+------------------------------------------+----------------------------------------------------------+
| 30478e1e193485cce93164e9877002b811acf950 | remove `SSH_KEY` parameter from `doctor-slave-parameter` |
+------------------------------------------+----------------------------------------------------------+
| 513b05275cbac2ff98950bb0a384a275dd8884f5 | Parpare ssh_key for MCP in doctor                        |
+------------------------------------------+----------------------------------------------------------+

Version change
^^^^^^^^^^^^^^

Module version changes
~~~~~~~~~~~~~~~~~~~~~~

- OpenStack has changed from Queens-1 to Rocky-1 since previous Gambia release.

Document version changes
~~~~~~~~~~~~~~~~~~~~~~~~

These documents have been updated in Hunter release

- Testing document
  docs/development/overview/testing.rst
- Doctor scenario in functest:
  docs/development/overview/functest_scenario/doctor-scenario-in-functest.rst

Reason for version
^^^^^^^^^^^^^^^^^^

Documentation is updated due to maintenance use case testing using Fenix.

Feature additions
~~~~~~~~~~~~~~~~~

+--------------------+----------------------------------------------------------+
| **JIRA REFERENCE** | **SLOGAN**                                               |
+--------------------+----------------------------------------------------------+
| DOCTOR-129         | Maintenance use case implementation in OpenStack Fenix   |
+--------------------+----------------------------------------------------------+
| DOCTOR-131         | Support Fenix and sample implementation accordingly      |
+--------------------+----------------------------------------------------------+
| DOCTOR-132         | Integrate with MCP                                       |
+--------------------+----------------------------------------------------------+
| DOCTOR-133         | Doctor fault management with notification from Inspector |
+--------------------+----------------------------------------------------------+

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
| INSTALLER_TYPE='Apex' 1)             | SUCCESS      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Fuel' 2)             | SUCCESS      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Local'               | N/A          |
+--------------------------------------+--------------+
1) Uses enhanced alarming worked in DOCTOR-133
2) Uses alarm from Nova reset server state API generated notification. API call
   can take a lot of time and alarm might take over a second. This also happens
   with different installer and for more Telco grade performance we need the
   enhanced alarming.

Doctor CI results with TEST_CASE='fault_management' and INSPECTOR_TYPE=congress
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex' 1)             | FAILED       |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Fuel'                | N/A          |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Local'               | N/A          |
+--------------------------------------+--------------+
1) Takes over one second because Nova reset server state error API is too slow

Doctor Functest results with TEST_CASE='fault_management'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex'                | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Fuel'                | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Local'               | N/A          |
+--------------------------------------+--------------+

Note: Installer Functest does not currently test features or skips running the
project test cases

Doctor CI results with TEST_CASE='maintenance'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex'                | SUCCESS      |
| ADMIN_TOOL_TYPE='sample'             |              |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex'                | SUCCESS      |
| ADMIN_TOOL_TYPE='fenix'              |              |
+--------------------------------------+--------------+

Doctor Functest results with TEST_CASE='maintenance'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

N/A - Needs special target environment with at least 3 compute nodes

References
==========

For more information about the OPNFV Doctor latest work, please see:

https://wiki.opnfv.org/display/doctor/Doctor+Home
