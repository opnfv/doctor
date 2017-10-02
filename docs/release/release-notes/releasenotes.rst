.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

======================================
OPNFV Doctor release notes (Euphrates)
======================================

This document provides an overview of the Doctor project in the OPNFV Euphrates
release, including new features, known issues and documentation updates.

Version history
===============

+------------+----------+------------+-------------+
| **Date**   | **Ver.** | **Author** | **Comment** |
+============+==========+============+=============+
| 2017-10-02 | 5.0.0    | Ryota Mibu |             |
+------------+----------+------------+-------------+

Important notes
===============

OPNFV Doctor project started as a requirement project and identified gaps
between "as-is" open source software (OSS) and an "ideal" platform for NFV.
Based on this analysis, the Doctor project proposed missing features to
upstream OSS projects. After those features were implemented, OPNFV installer
projects integrated the features to the OPNFV platform and the OPNFV
infra/testing projects verified the functionalities in the OPNFV Labs.

For Euphrates release, the Doctor project focused primarily on refactoring
testing code by python, which improves readability and maintenancebility of
the testing code in the Doctor repository.

New features
============

Doctor now supports network state handling where VIM tells you the actual data
plane port state, utilizing the new feature called `port-dp-status`_ developed
in OpenStack Neutron as the result of our upstreaming efforts.

.. _port-data-plane-status: https://specs.openstack.org/openstack/neutron-specs/specs/backlog/ocata/port-data-plane-status.html

Installer support and verification status
=========================================

Integrated features
-------------------

The testing code for doctor test cases are enhanced by refactoring in python,
and supporting collectd monitor.
Developers, who are refereeing OPNFV, can understand and reuse the doctor
testing code easily, comparing to the one written in bash script.

From the Euphrates release, key integrated feature is:

* **collectd as Doctor Monitor**

 This is experimental, as CI job is not enabled yet. But, you can see and test
 with collectd integrated in Doctor reference archetecture.

OPNFV installer support matrix
------------------------------

(TBC)

In the Brahmaputra release, only one installer (Apex) supported the deployment
of the basic Doctor framework by configuring Doctor features. In the Euphrates
release, integration of Doctor features progressed in other OPNFV installers.

+-----------+-------------------+--------------+-----------------+-------------------+
| Installer | Aodh              | Nova: Force  | Nova: Get valid | Congress          |
|           | integration       | compute down | service status  | integration       |
+===========+===================+==============+=================+===================+
| Apex      | Available         | Available    | Available,      | Available         |
|           |                   |              | Verified only   |                   |
|           |                   |              | for admin users |                   |
+-----------+-------------------+--------------+-----------------+-------------------+
| Fuel      | Available         | Available    | Available,      | N/A               |
|           | (`DOCTOR-58`_)    |              | Verified only   | (`FUEL-230`_)     |
|           |                   |              | for admin users |                   |
+-----------+-------------------+--------------+-----------------+-------------------+
| Joid      | Available         | TBC          | TBC             | Available         |
|           | (`JOID-76`_),     |              |                 | (`JOID-73`_),     |
|           | Not verified      |              |                 | Not verified      |
+-----------+-------------------+--------------+-----------------+-------------------+
| Compass   | Available         | TBC          | TBC             | Available         |
|           | (`COMPASS-357`_), |              |                 | (`COMPASS-367`_), |
|           | Not verified      |              |                 | Not verified      |
+-----------+-------------------+--------------+-----------------+-------------------+

.. _DOCTOR-58: https://jira.opnfv.org/browse/DOCTOR-58
.. _FUEL-230: https://jira.opnfv.org/browse/FUEL-230
.. _JOID-76: https://jira.opnfv.org/browse/JOID-76
.. _JOID-73: https://jira.opnfv.org/browse/JOID-73
.. _COMPASS-357: https://jira.opnfv.org/browse/COMPASS-357
.. _COMPASS-367: https://jira.opnfv.org/browse/COMPASS-367

Note: 'Not verified' means that we didn't verify the functionality by having
our own test scenario running in OPNFV CI pipeline yet.

Documentation updates
=====================

* **maintenance detailed spec**

  The maintenance design document was filed, including suggestions how to
  leverage features in OpenStack while developing automated maintenance
  capability.

* **Inspector design guideline**

Known issues
============

* Testing code for `port-data-plane-status` in Doctor repository was disabled
  in 5.0, as we have problem in neutron client load in CI job container.
