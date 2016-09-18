.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

=====================================
OPNFV Doctor Release Notes (Colorado)
=====================================

Version History
===============

+------------+--------------+------------+-------------+
| **Date**   | **Ver.**     | **Author** | **Comment** |
+============+==============+============+=============+
| 2016-09-19 | Colorado 1.0 | Ryota Mibu |             |
+------------+--------------+------------+-------------+

Important Notes
===============

OPNFV Doctor project started as a requirement project and identified gaps
between as-is open source software (OSS) and ideal platform for NFV.
Based on this analysis, Doctor project proposed missing features to
upstream OSS projects. After those features were implemented, OPNFV installer
projects integrated the features to OPNFV platform, also OPNFV infra/testing
projects verified the functionalities in OPNFV Labs.

This document provides overview of Doctor project in OPNFV Colorado release,
including new features, known issues and docmentation updates.

New Features
============

Congress as a Doctor Inspector
------------------------------

Since Doctor driver in OpenStack Congress has been implemented in Mitaka,
OpenStack Congress can now take a role of Doctor Inspector which correlates
an error of physical resource to effected virtual resource(s) immediately.

Installer Supports and Verification Status
==========================================

Integrated features
-------------------

Minimal Doctor functionality of VIM are available in OPNFV platform from
Brahmaputra release. The basic doctor framework in VIM consists of Controller
(Nova) and Notifier(Ceilometer+Aodh) along with sample Inspector and Monitor
developed by Doctor team. From Colorado release, key integrated features are;

- Immediate notification upon state update of virtual resource enabled by
  Ceilometer and Aodh (Aodh Integration)

- Consistent state awareness improved by exposing host status in server (VM)
  information via Nova API (Get vaild sevice status)

- OpenStack Congress enabling policy-based flexible failre correlation
  (Congress Integration)

OPNFV Installer Support Matrix
------------------------------

In Brahmaputra release, only one installer (Apex) supported to deploy this
basic doctor framework by configuring Doctor features. In Colorado release,
integration of Doctor features progressed in other OPNFV installers.

+-----------+------------------+--------------------------+----------------------+
| Installer | Aodh Integration | Get vaild service status | Congress Integration |
+===========+==================+==========================+======================+
| Apex      | Available        | Available                | Available,           |
|           |                  | `DOCTOR-67`_             | Not Verified         |
|           |                  |                          | `APEX-135`_          |
|           |                  |                          | `APEX-158`_          |
+-----------+------------------+--------------------------+----------------------+
| Fuel      | Available,       | Available                | Available,           |
|           | Not Verified     |                          | Not Verified         |
|           | `DOCTOR-58`_     |                          | `FUEL-119`_          |
+-----------+------------------+--------------------------+----------------------+
| Joid      | Available,       | TBC                      | Available,           |
|           | Not Verified     |                          | Not Verified         |
|           | `JOID-76`_       |                          | `JOID-73`_           |
+-----------+------------------+--------------------------+----------------------+
| Compass   | Available,       | TBC                      | N/A                  |
|           | Not Verified     |                          | `COMPASS-367`_       |
|           | `COMPASS-357`_   |                          |                      |
+-----------+------------------+--------------------------+----------------------+

.. _DOCTOR-67: https://jira.opnfv.org/browse/DOCTOR-67
.. _APEX-135: https://jira.opnfv.org/browse/APEX-135
.. _APEX-158: https://jira.opnfv.org/browse/APEX-158
.. _DOCTOR-58: https://jira.opnfv.org/browse/DOCTOR-58
.. _FUEL-119: https://jira.opnfv.org/browse/FUEL-119
.. _JOID-76: https://jira.opnfv.org/browse/JOID-76
.. _JOID-73: https://jira.opnfv.org/browse/JOID-73
.. _COMPASS-357: https://jira.opnfv.org/browse/COMPASS-357
.. _COMPASS-367: https://jira.opnfv.org/browse/COMPASS-367

Note: 'Not Verified' means that we didn't verify the functionality by having
our own test scenario running in OPNFV CI pipeline yet.

Documentation Updates
=====================

Alarm Comparison
----------------

The report of gap analysis accross alarm specifications in ETSI NFV IFA, OPNFV
Doctor and OpenStack Aodh is added, along with some proposals (`DOCTOR-46`_).
This enables us to improve alignment between SDO specification and OSS
implementation as a future work.

.. _DOCTOR-46: https://jira.opnfv.org/browse/DOCTOR-46

Description of test scenario
----------------------------

Description of Doctor scenario, which is running as one of feature verification
scenario in Functest, is updated (`DOCTOR-53`_).

.. _DOCTOR-53: https://jira.opnfv.org/browse/DOCTOR-53

Neutron Port Status Update
--------------------------

Design documentation for port status update is added, intending to propose
new feature to OpenStack Neutron.

SB I/F Specification
--------------------

The initial specification of Doctor southbound interface, which is for
Inspector to receive event meesages from Monitors, is added (`DOCTOR-17`_).

.. _DOCTOR-17: https://jira.opnfv.org/browse/DOCTOR-17

Know Issues
===========

Aodh 'event-alarm' is not available in default (Fuel)
-----------------------------------------------------

In Fuel 9.0, Aodh Integration for 'event-alarm' is not completed. You can use
`fuel-plugin-doctor`_ to correct ceilometer configuration as a workaround.
See `DOCTOR-62`_.

.. _fuel-plugin-doctor: https://github.com/openzero-zte/fuel-plugin-doctor
.. _DOCTOR-62: https://jira.opnfv.org/browse/DOCTOR-62

Performance issue in correct resource status (Fuel)
---------------------------------------------------

Although doctor project is aming to make the time interval between detection
and notification to user less than 1 second, we observed that it takes more
than 2 second in default OPNFV deployment using fuel installer [*]_.
This issue will be solved by checking OpenStack configuration and improving
Doctor testing scenario.

.. _[*]: http://lists.opnfv.org/pipermail/opnfv-tech-discuss/2016-September/012542.html
