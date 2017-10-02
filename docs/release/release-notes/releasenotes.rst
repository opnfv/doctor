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

This document provides an overview of the Doctor project in the OPNFV Euphrates
release, including new features, known issues and documentation updates.

New features
============

Doctor now supports network state handling where VIM notifies on the actual data
plane port state, utilizing the new feature called `port-dp-status`_ developed
in OpenStack Neutron as the result of our upstreaming efforts.

.. _port-data-plane-status: https://specs.openstack.org/openstack/neutron-specs/specs/backlog/ocata/port-data-plane-status.html

For Euphrates release, the Doctor project also refactored testing code to python.


Installer support and verification status
=========================================

Integrated features
-------------------

The testing code for Doctor test cases are enhanced by refactoring to python,
and supporting collectd monitor.

The python refactoring improves readability and maintainability of the testing
code in the Doctor repository. This helps Doctor developers as well as
engineers who are interested in OPNFV Doctor.

From the Euphrates release, key integrated feature is:

* **collectd as Doctor Monitor**

  Collectd was added as additional Doctor monitoring solution.
  This is experimental, as CI job is not enabled yet. But, you can see and test
  with collectd integrated in Doctor reference architecture.

OPNFV installer support matrix
------------------------------

+-----------+-------------------+----------------+-----------------+-------------------+
| Installer | Aodh              | Nova: Force    | Nova: Get valid | Congress          |
|           | integration       | compute down   | service status  | integration       |
+===========+===================+================+=================+===================+
| Apex      | Available         | Available      | Available       | Available         |
+-----------+-------------------+----------------+-----------------+-------------------+
| Fuel/MCP  | Available         | Available      | Available       | N/A               |
|           | (`DOCTOR-58`_)    | (not verified) | (not verified)  |                   |
+-----------+-------------------+----------------+-----------------+-------------------+
| Joid      | Available         | TBC            | TBC             | Available         |
|           | (`JOID-76`_),     |                |                 | (`JOID-73`_),     |
|           | Not verified      |                |                 | Not verified      |
+-----------+-------------------+----------------+-----------------+-------------------+
| Compass   | Available         | TBC            | TBC             | Available         |
|           | (`COMPASS-357`_), |                |                 | (`COMPASS-367`_), |
|           | Not verified      |                |                 | Not verified      |
+-----------+-------------------+----------------+-----------------+-------------------+

.. _DOCTOR-58: https://jira.opnfv.org/browse/DOCTOR-58
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

  The documentation on the Inspector design has been updated to include
  guidelines on the 'host specific VMs list', 'parallel execution', and 'shortcut notification'.

Known issues
============

* Testing code for `port-data-plane-status` in Doctor repository was disabled
  in 5.0.0, as we have problem in neutron client load in CI job container.
