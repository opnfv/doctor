.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Gambia of Doctor.

Important notes
===============

In Gambia release, Doctor has been working with our second use case over
maintenance. Design guideline is now done and test case exists with sample
maintenance workflow code implemented in Doctor. Work has also started to have
the real implementation done in the OpenStack Fenix project
https://wiki.openstack.org/wiki/Fenix.

Doctor CI testing has now moved to use tox on jumphots instead of running test
through features container. Also in Apex we use OpenStack services running in
containers. Functest daily testing supports Doctor fault management test case
for Apex, Daisy and Fuel installers. This testing is done through features
container.

In this release, Doctor has not been working with the fault management use case as
the basic framework has been already done. However, we might need to get back to
it later to better meet the tough industry requirements as well as requirements
from edge, containers and 5G.


Summary
=======

Gambia Doctor framework uses OpenStack Queens integrated into its test cases.
Compared to the previous release, the Heat project is also being used in the
maintenance test case.

Release Data
============

Doctor changes

+------------------------------------------+----------------------------------------------------------+
| **commit-ID**                            | **Subject**                                              |
+------------------------------------------+----------------------------------------------------------+
| 5b3f5937e7b861fca46b2a6b2d6708866b800f95 | fix building docs                                        |
+------------------------------------------+----------------------------------------------------------+
| 2ca5924081ce4784f599437707bd32807aa155ce | Fix SSH client connection reset                          |
+------------------------------------------+----------------------------------------------------------+
| baac6579556f8216b36db0d0f87f9c2d4f8b4ef5 | Support Apex with services in containers                 |
+------------------------------------------+----------------------------------------------------------+
| 23bf63c4616040cb0d69cd26238af2a4a7c00a90 | fix the username to login undercloud in Apex             |
+------------------------------------------+----------------------------------------------------------+
| 61eb3927ada784cc3dffb5ddd17f66e47871f708 | Local Documentation Builds                               |
+------------------------------------------+----------------------------------------------------------+
| 0f1dd4314b9e0247d9af7af6df2410462423aeca | Updated from global requirements                         |
+------------------------------------------+----------------------------------------------------------+
| 2d4a9f0c0a93797da6534583f6e74553a4b634be | Fix links to remove references to submodules             |
+------------------------------------------+----------------------------------------------------------+
| 3ddc2392b0ed364eede49ff006d64df3ea456350 | Gambia release notes                                     |
+------------------------------------------+----------------------------------------------------------+
| 825a0a0dd5e8028129b782ed21c549586257b1c5 | delete doctor datasource in congress when cleanup        |
+------------------------------------------+----------------------------------------------------------+
| fcf53129ab2b18b84571faff13d7cb118b3a41b3 | run profile even the notification time is larger than 1S |
+------------------------------------------+----------------------------------------------------------+
| 495965d0336d42fc36494c81fd15cee2f34c96e9 | Update and add test case                                 |
+------------------------------------------+----------------------------------------------------------+
| da25598a6a31abe0579ffed12d1719e5ff75f9a7 | bugfix: add doctor datasource in congress                |
+------------------------------------------+----------------------------------------------------------+
| f9e1e3b1ae4be80bc2dc61d9c4213c81c091ea72 | Update the maintenance design document                   |
+------------------------------------------+----------------------------------------------------------+
| 4639f15e6db2f1480b41f6fbfd11d70312d4e421 | Add maintenance test code                                |
+------------------------------------------+----------------------------------------------------------+
| b54cbc5dd2d32fcb27238680b4657ed384d021c5 | Add setup and cleanup for maintenance test               |
+------------------------------------------+----------------------------------------------------------+
| b2bb504032ac81a2ed3f404113b097d9ce3d7f14 | bugfix: kill the stunnel when cleanup                    |
+------------------------------------------+----------------------------------------------------------+
| eaeb3c0f9dc9e6645a159d0a78b9fc181fce53d4 | add ssh_keyfile for connect to installer in Apex         |
+------------------------------------------+----------------------------------------------------------+
| dcbe7bf1c26052b0e95d209254e7273aa1eaace1 | Add tox and test case to testing document                |
+------------------------------------------+----------------------------------------------------------+
| 0f607cb5efd91ee497346b7f792dfa844d15595c | enlarge the time of link down                            |
+------------------------------------------+----------------------------------------------------------+
| 1351038a65739b8d799820de515178326ad05f7b | bugfix: fix the filename of ssh tunnel                   |
+------------------------------------------+----------------------------------------------------------+
| e70bf248daac03eee6b449cd1654d2ee6265dd8c | Use py34 instead of py35                                 |
+------------------------------------------+----------------------------------------------------------+
| 2a60d460eaf018951456451077b7118b60219b32 | add INSPECTOR_TYPE and TEST_CASE to tox env              |
+------------------------------------------+----------------------------------------------------------+
| 2043ceeb08c1eca849daeb2b3696d385425ba061 | [consumer] fix default value for port number             |
+------------------------------------------+----------------------------------------------------------+

Releng changes

+------------------------------------------+-----------------------------------------------------------------------+
| **commit-ID**                            | **Subject**                                                           |
+------------------------------------------+-----------------------------------------------------------------------+
| c87309f5a75ccc5d595f708817b97793c24c4387 | Add Doctor maintenance job                                            |
+------------------------------------------+-----------------------------------------------------------------------+
| bd16a9756ffd0743e143f0f2f966da8dd666c7a3 | remove congress test in Daisy                                         |
+------------------------------------------+-----------------------------------------------------------------------+
| c47aaaa53c91aae93877f2532c72374beaa4eabe | remove fuel job in Doctor                                             |
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

These documents have been updated in Gambia release

- Testing document
  docs/development/overview/testing.rst
- Doctor scenario in functest
  docs/development/overview/functest_scenario/doctor-scenario-in-functest.rst
- Maintenance design guideline
  docs/development/design/maintenance-design-guideline.rst

Reason for version
^^^^^^^^^^^^^^^^^^

Documentation is updated due to tox usage in testing and adding maintenance
use case related documentation.

Feature additions
~~~~~~~~~~~~~~~~~

+--------------------+--------------------------------------------------------+
| **JIRA REFERENCE** | **SLOGAN**                                             |
+--------------------+--------------------------------------------------------+
| DOCTOR-106         | Maintenance scenario                                   |
+--------------------+--------------------------------------------------------+
| DOCTOR-125         | Maintenance design document according to our test case |
+--------------------+--------------------------------------------------------+
| DOCTOR-126         | Use Tox instead of Functest for doctor CI jobs         |
+--------------------+--------------------------------------------------------+
| DOCTOR-127         | Maintenance test POD                                   |
+--------------------+--------------------------------------------------------+
| DOCTOR-130         | Apex with containers                                   |
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

Doctor CI results with TEST_CASE='fault_management' and INSPECTOR_TYPE=sample
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex'                | SUCCESS      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Compass'             | N/A          |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Daisy'               | SUCCESS      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Fuel'                | No POD       |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Joid'                | N/A          |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Local'               | N/A          |
+--------------------------------------+--------------+

Doctor CI results with TEST_CASE='fault_management' and INSPECTOR_TYPE=congress
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+--------------+
| **TEST-SUITE**                       | **Results:** |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Apex'                | FAILED       |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Compass'             | N/A          |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Daisy'               | N/A          |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Fuel'                | No POD       |
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
| INSTALLER_TYPE='Compass'             | N/A          |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Daisy'               | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Fuel'                | skipped      |
+--------------------------------------+--------------+
| INSTALLER_TYPE='Joid'                | N/A          |
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
+--------------------------------------+--------------+

Doctor Functest results with TEST_CASE='maintenance'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

N/A - Needs special target and currently there is only sample implementation

References
==========

For more information about the OPNFV Doctor latest work, please see:

https://wiki.opnfv.org/display/doctor/Doctor+Home
