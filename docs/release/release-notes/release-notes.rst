.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Gambia of Doctor.

.. contents::
   :depth: 3
   :local:


Version history
---------------

+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
+--------------------+--------------------+--------------------+--------------------+
| 2018-08-07         | 7.0.0              | Tomi Juvonen       | First draft        |
+--------------------+--------------------+--------------------+--------------------+

Important notes
===============

In Gambia release Doctor has been working with our second use case over
maintenance. Design guideline is now done and test case exist with sample
maintenance workflow code implemented in Doctor. Work has also started to have
the real implementation done in the OpenStack Fenix project.

Doctor CI testing has now moved to use tox instead of Functest.

In this release Doctor has not been working with the fault management use case as
the basic framework has been already done. However we might need to get back to
it later to better meet the tough industry requirements as well as requirements
from edge, containers and 5G.


Summary
=======

Gambia Doctor framework uses OpenStack Queens integrated to its test cases.
Compared to the previous release, the Heat project is also being used in the
maintenance test case.

Release Data
============

**TBD - tox, documents and maintenance test case changes coming**

Doctor changes

+------------------------------------------+----------------------------------------------+
| **commit-ID**                            | **Subject**                                  |
+------------------------------------------+----------------------------------------------+
| 1351038a65739b8d799820de515178326ad05f7b | bugfix: fix the filename of ssh tunnel       |
+------------------------------------------+----------------------------------------------+
| e70bf248daac03eee6b449cd1654d2ee6265dd8c | Use py34 instead of py35                     |
+------------------------------------------+----------------------------------------------+
| 2a60d460eaf018951456451077b7118b60219b32 | add INSPECTOR_TYPE and TEST_CASE to tox env  |
+------------------------------------------+----------------------------------------------+
| 2043ceeb08c1eca849daeb2b3696d385425ba061 | [consumer] fix default value for port number |
+------------------------------------------+----------------------------------------------+

Releng changes

+------------------------------------------+-----------------------------------------------------------------------+
| **commit-ID**                            | **Subject**                                                           |
+------------------------------------------+-----------------------------------------------------------------------+
| ab2fed2522eaf82ea7c63dd05008a37c56e825d0 | use 'workspace-cleanup' plugin in publisher                           |
+------------------------------------------+-----------------------------------------------------------------------+
| 3aaed5cf40092744f1b87680b9205a2901baecf3 | clean the workspace in the publisher                                  |
+------------------------------------------+-----------------------------------------------------------------------+
| 50151eb3717edd4ddd996f3705fbe1732de7f3b7 | run tox with 'sudo'                                                   |
+------------------------------------------+-----------------------------------------------------------------------+
| a3adc85ecb52f5d19ec4e9c49ca1ac35aa429ff9 | remove inspector variable form job template                           |
+------------------------------------------+-----------------------------------------------------------------------+
| adfbaf2a3e8487e4c9152bf864a653a0425b8582 | run doctor tests with different inspectors in sequence                |
+------------------------------------------+-----------------------------------------------------------------------+
| 2e98e56224cd550cb3bf9798e420eece28139bd9 | add the ssh_key info if the key_file is exist                         |
+------------------------------------------+-----------------------------------------------------------------------+
| c109c271018e9a85d94be1b9b468338d64589684 | prepare installer info for doctor test                                |
+------------------------------------------+-----------------------------------------------------------------------+
| 57cbefc7160958eae1d49e4753779180a25864af | use py34 for tox                                                      |
+------------------------------------------+-----------------------------------------------------------------------+
| 3547754e808a581b09c9d22e013a7d986d9f6cd1 | specify the cacert file when it exits                                 |
+------------------------------------------+-----------------------------------------------------------------------+
| ef4f36aa1c2ff0819d73cde44f84b99a42e15c7e | bugfix: wrong usage of '!include-raw'                                 |
+------------------------------------------+-----------------------------------------------------------------------+
| af9396beb5d068cd3b2a1a74c97287b8f0760644 | bugfix: wrong usage of '!include-raw'                                 |
+------------------------------------------+-----------------------------------------------------------------------+
| 0e0e0d4cb71fb27b1789a2bef2d3c4ff313e67ff | use tox instead of functest for doctor CI jobs                        |
+------------------------------------------+-----------------------------------------------------------------------+
| 5b22f1b95feacaec0380f6a7543cbf510b628451 | pass value to parameters                                              |
+------------------------------------------+-----------------------------------------------------------------------+
| 44ab0cea07fa2a734c4f6b80776ad48fd006d1b8 | Doctor job bugfix: fix the scenario                                   |
+------------------------------------------+-----------------------------------------------------------------------+
| 17617f1c0a78c7bdad0d11d329a6c7e119cbbddd | bugfix: run doctor tests parallelly                                   |
+------------------------------------------+-----------------------------------------------------------------------+
| 811e4ef7f4c37b7bc246afc34ff880c014ecc05d | delete 'opnfv-build-ubuntu-defaults' parameters for doctor verify job |
+------------------------------------------+-----------------------------------------------------------------------+
| 0705f31ab5bc54c073df120cbe0fe62cf10f9a81 | delete the 'node' parameter in 'doctor-slave-parameter' macro         |
+------------------------------------------+-----------------------------------------------------------------------+
| 304151b15f9d7241db8c5fea067cafe048287d84 | fix the default node label for doctor test                            |
+------------------------------------------+-----------------------------------------------------------------------+
| a6963f92f015a33b44b27199886952205499b44c | Fix project name                                                      |
+------------------------------------------+-----------------------------------------------------------------------+
| f122bfed998b3b0e0178106a7538377c609c6512 | add a default value for SSH_KEY                                       |
+------------------------------------------+-----------------------------------------------------------------------+


Version change
^^^^^^^^^^^^^^

Module version changes
~~~~~~~~~~~~~~~~~~~~~~

- OpenStack has changed from Pike-1 to Queens-1

Document version changes
~~~~~~~~~~~~~~~~~~~~~~~~

**TBD - following are coming**
-Testing document
-Doctor scenario in functest
-Maintenance design guideline

Reason for version
^^^^^^^^^^^^^^^^^^

Documentation is updated due to tox usage in testing and adding maintenance
use case related documentation.

Feature additions
~~~~~~~~~~~~~~~~~

**TBD - tox, these JIRA tickets are expected to be finished**

+--------------------+--------------------------------------------------------+
| **JIRA REFERENCE** | **SLOGAN**                                             |
+--------------------+--------------------------------------------------------+
| DOCTOR-106         | Maintenance scenario                                   |
+--------------------+--------------------------------------------------------+
| DOCTOR-125         | Maintenance design document according to our test case |
+--------------------+--------------------------------------------------------+
| DOCTOR-126         | Use Tox instead of Functest for doctor CI jobs         |
+--------------------+--------------------------------------------------------+


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

**TBD, CI with tox needs still Fuel and Apex to work**

Doctor CI results with TEST_CASE='fault_management' and INSPECTOR_TYPE=sample
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex'                | FAILED       |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Compass'             | N/A          |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Daisy'               | SUCCESS      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Fuel'                | FAILED       |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Joid'                | N/A          |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Local'               | N/A          |
+--------------------------------------+--------------+

Doctor Functest results with TEST_CASE='fault_management'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex'                | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Compass'             | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Daisy'               | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Fuel'                | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Joid'                | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Local'               | skipped      |
+--------------------------------------+--------------+

Note: Installer Functest does not currently test features or skips running the
project test cases

Doctor CI results with TEST_CASE='maintenance'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**TBD, we need to have Apex env for testing**

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex'                | N/A          |
+--------------------------------------+--------------+

Doctor Functest results with TEST_CASE='maintenance'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

N/A - Needs special target and currently there is only sample implementation

References
==========

For more information about the OPNFV Doctor latest work, please see:

https://wiki.opnfv.org/display/doctor/Doctor+Home
