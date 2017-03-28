.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

=====================================
OPNFV Doctor release notes (Colorado)
=====================================

Version history
===============

+------------+--------------+------------+-------------+
| **Date**   | **Ver.**     | **Author** | **Comment** |
+============+==============+============+=============+
| 2016-09-19 | Colorado 1.0 | Ryota Mibu |             |
+------------+--------------+------------+-------------+

Important notes
===============

OPNFV Doctor project started as a requirement project and identified gaps
between "as-is" open source software (OSS) and an "ideal" platform for NFV.
Based on this analysis, the Doctor project proposed missing features to
upstream OSS projects. After those features were implemented, OPNFV installer
projects integrated the features to the OPNFV platform and the OPNFV
infra/testing projects verified the functionalities in the OPNFV Labs.

This document provides an overview of the Doctor project in the OPNFV Colorado
release, including new features, known issues and documentation updates.

New features
============

* **Congress as a Doctor Inspector**

  Since `Doctor driver`_ in OpenStack Congress has been implemented in Mitaka,
  OpenStack Congress can now take the role of the Doctor Inspector to correlate
  an error in a physical resource to the affected virtual resource(s)
  immediately.

.. _Doctor driver: https://review.openstack.org/#/c/314915/

Installer support and verification status
=========================================

Integrated features
-------------------

Minimal Doctor functionality of VIM is available in the OPNFV platform from
the Brahmaputra release. The basic Doctor framework in VIM consists of a
Controller (Nova) and a Notifier (Ceilometer+Aodh) along with a sample
Inspector and Monitor developed by the Doctor team.
From the Colorado release, key integrated features are:

* Immediate notification upon state update of virtual resource enabled by
  Ceilometer and Aodh (Aodh integration)

* Consistent state awareness improved by having nova API to mark nova-compute
  service down (Nova: Force compute down)

* Consistent state awareness improved by exposing host status in server (VM)
  information via Nova API (Nova: Get valid service status)

* OpenStack Congress enabling policy-based flexible failure correlation
  (Congress integration)

OPNFV installer support matrix
------------------------------

In the Brahmaputra release, only one installer (Apex) supported the deployment
of the basic doctor framework by configuring Doctor features. In the Colorado
release, integration of Doctor features progressed in other OPNFV installers.

+-----------+-------------------+--------------+-----------------+------------------+
| Installer | Aodh              | Nova: Force  | Nova: Get valid | Congress         |
|           | integration       | compute down | service status  | integration      |
+===========+===================+==============+=================+==================+
| Apex      | Available         | Available    | Available       | Available        |
|           |                   |              | (`DOCTOR-67`_), | (`APEX-135`_,    |
|           |                   |              | Verified only   | `APEX-158`_),    |
|           |                   |              | for admin users | Not Verified     |
+-----------+-------------------+--------------+-----------------+------------------+
| Fuel      | Available         | Available    | Available,      | N/A              |
|           | (`DOCTOR-58`_),   |              | Verified only   | (`FUEL-119`_)    |
|           | Not verified      |              | for admin users |                  |
+-----------+-------------------+--------------+-----------------+------------------+
| Joid      | Available         | TBC          | TBC             | TBC              |
|           | (`JOID-76`_),     |              |                 | (`JOID-73`_)     |
|           | Not verified      |              |                 |                  |
+-----------+-------------------+--------------+-----------------+------------------+
| Compass   | Available         | TBC          | TBC             | N/A              |
|           | (`COMPASS-357`_), |              |                 | (`COMPASS-367`_) |
|           | Not verified      |              |                 |                  |
+-----------+-------------------+--------------+-----------------+------------------+

.. _DOCTOR-67: https://jira.opnfv.org/browse/DOCTOR-67
.. _APEX-135: https://jira.opnfv.org/browse/APEX-135
.. _APEX-158: https://jira.opnfv.org/browse/APEX-158
.. _DOCTOR-58: https://jira.opnfv.org/browse/DOCTOR-58
.. _FUEL-119: https://jira.opnfv.org/browse/FUEL-119
.. _JOID-76: https://jira.opnfv.org/browse/JOID-76
.. _JOID-73: https://jira.opnfv.org/browse/JOID-73
.. _COMPASS-357: https://jira.opnfv.org/browse/COMPASS-357
.. _COMPASS-367: https://jira.opnfv.org/browse/COMPASS-367

Note: 'Not verified' means that we didn't verify the functionality by having
our own test scenario running in OPNFV CI pipeline yet.

Documentation updates
=====================

* **Alarm comparison**

  A report on the gap analysis across alarm specifications in ETSI NFV IFA,
  OPNFV Doctor and OpenStack Aodh has been added, along with some proposals
  on how to improve the alignment between SDO specification and OSS
  implementation as a future work (`DOCTOR-46`_).

.. _DOCTOR-46: https://jira.opnfv.org/browse/DOCTOR-46

* **Description of test scenario**

  The description of the Doctor scenario, which is running as one of the
  feature verification scenarios in Functest, has been updated (`DOCTOR-53`_).

.. _DOCTOR-53: https://jira.opnfv.org/browse/DOCTOR-53

* **Neutron port status update**

  Design documentation for port status update has been added, intending to
  propose new features to OpenStack Neutron.

* **SB I/F specification**

  The initial specification of the Doctor southbound interface, which is for
  the Inspector to receive event messages from Monitors, has been added
  (`DOCTOR-17`_).

.. _DOCTOR-17: https://jira.opnfv.org/browse/DOCTOR-17

Known issues
============

* **Aodh 'event-alarm' is not available as default (Fuel)**

  In Fuel 9.0, Aodh integration for 'event-alarm' is not completed.
  Ceilometer and Nova would be mis-configured and cannot pass event
  notification to Aodh.
  You can use `fuel-plugin-doctor`_ to correct Ceilometer and Nova
  configuration as a workaround. See `DOCTOR-62`_.

.. _fuel-plugin-doctor: https://github.com/openzero-zte/fuel-plugin-doctor
.. _DOCTOR-62: https://jira.opnfv.org/browse/DOCTOR-62

* **Security notice**

  Security notice has been raised in [*]_. Please insure that the debug option
  of Flask is set to False, before running in production.

.. [*] http://lists.opnfv.org/pipermail/opnfv-tech-discuss/2016-September/012610.html

* **Performance issue in correct resource status (Fuel)**

  Although the Doctor project is aiming to ensure that the time interval
  between detection and notification to the user is less than 1 second, we
  observed that it takes more than 2 seconds in the default OPNFV deployment
  using the Fuel installer [*]_.
  This issue will be solved by checking the OpenStack configuration and
  improving Doctor testing scenario.

.. [*] http://lists.opnfv.org/pipermail/opnfv-tech-discuss/2016-September/012542.html
