.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

=====================================
OPNFV Doctor release notes (Danube)
=====================================

Version history
===============

+------------+--------------+------------+-------------+
| **Date**   | **Ver.**     | **Author** | **Comment** |
+============+==============+============+=============+
| 2016-XX-XX | Danube 1.0   | ...        |             |
+------------+--------------+------------+-------------+

Important notes
===============

OPNFV Doctor project started as a requirement project and identified gaps
between "as-is" open source software (OSS) and an "ideal" platform for NFV.
Based on this analysis, the Doctor project proposed missing features to
upstream OSS projects. After those features were implemented, OPNFV installer
projects integrated the features to the OPNFV platform and the OPNFV
infra/testing projects verified the functionalities in the OPNFV Labs.

This document provides an overview of the Doctor project in the OPNFV Danube
release, including new features, known issues and documentation updates.

New features
============

* **FEATURE 1**

  TODO: add description including pointer to `feature1`_ and explain what it is about.

.. _feature1: https://review.openstack.org/#/c/....../

Installer support and verification status
=========================================

Integrated features
-------------------

Minimal Doctor functionality of VIM is available in the OPNFV platform from
the Brahmaputra release. The basic Doctor framework in VIM consists of a
Controller (Nova) and a Notifier (Ceilometer+Aodh) along with a sample
Inspector and Monitor developed by the Doctor team.

From the Danube release, key integrated features are:

* ...

* ...

OPNFV installer support matrix
------------------------------

In the Brahmaputra release, only one installer (Apex) supported the deployment
of the basic doctor framework by configuring Doctor features. In the Danube
release, integration of Doctor features progressed in other OPNFV installers.

TODO: TABLE TO BE UPDATED!

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

* **Update 1**

  Description including pointer to JIRA ticket (`DOCTOR-46`_).

.. _DOCTOR-46: https://jira.opnfv.org/browse/DOCTOR-46


Known issues
============

* ...
