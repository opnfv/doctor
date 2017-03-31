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
| 2017-03-31 | Danube 1.0   | Ryota Mibu |             |
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

For Danube release, the Doctor project focused primarily on enhancing the
testing tools, enabling additional test scenarios, and support and verification
on a wider range of OPNFV installers.

* **Performance profiler PoC**

  The performance profiler is designed to get timestamp in each checkpoint of
  components for further analysis. In Danube, initial PoC implementation of the
  perfomance profiler has been added to the Doctor testing tools
  by contribution from the `QTIP`_ team. The tools can now show how long it
  takes for each component in a series of processes for fault notification.
  Some checkpoints are not covered yet though. To activate this, set the
  PROFILER_TYPE="poc" before running the main script ("tests/run.sh").
  See `DOCTOR-72`_ for more details.

* **Testing with multiple tenant VMs**

  The Doctor testing tools now supports new testing scenario where multiple
  tenant VMs in the system under test can be created (`DOCTOR-77`_).
  This allows to measure fault notification time/cost with stressed VIM
  controllers, in order to see perfomance trends.

.. _QTIP: https://wiki.opnfv.org/display/qtip
.. _DOCTOR-72: https://jira.opnfv.org/browse/DOCTOR-72
.. _DOCTOR-77: https://jira.opnfv.org/browse/DOCTOR-77

Installer support and verification status
=========================================

Integrated features
-------------------

Minimal Doctor functionality of VIM is available in the OPNFV platform from
the Brahmaputra release. The basic Doctor framework in VIM consists of a
Controller (Nova) and a Notifier (Ceilometer+Aodh) along with a sample
Inspector and Monitor developed by the Doctor team.

From the Danube release, key integrated feature is:

* **Congress as Doctor Inspector**

  Congress Inspector is now verified with latest vanilla OpenStack without
  backporting any patch, like the one we had backported for adding Doctor
  driver of Congress in Colorado.

OPNFV installer support matrix
------------------------------

In the Brahmaputra release, only one installer (Apex) supported the deployment
of the basic Doctor framework by configuring Doctor features. In the Danube
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

* **Configuration manual for Congress**

  Steps to configure Congress as Doctor Inspector have been added
  to Doctor configuration manual (`DOCTOR-85`_).

* **Alarm comparison**

  As part of the review between Doctor Danube (OpenStack Newton) and ETSI NFV
  IFA, the alarm comparison table has been updated (`DOCTOR-82`_).

* **OpenStack mechanisms for fencing**

  The section on fencing in the requirement document has been updated with more
  details of Nova and Neutron (`REVIEW#27049`_).

* **How to test**

  Two ways to run the Doctor testing tools have been added
  (`REVIEW#28223`_).

You can also find other minor updates in `DOCTOR-81`_.

.. _DOCTOR-81: https://jira.opnfv.org/browse/DOCTOR-81
.. _DOCTOR-82: https://jira.opnfv.org/browse/DOCTOR-82
.. _DOCTOR-85: https://jira.opnfv.org/browse/DOCTOR-85
.. _REVIEW#28223: https://gerrit.opnfv.org/gerrit/28223/
.. _REVIEW#27049: https://gerrit.opnfv.org/gerrit/27049/

Known issues
============

* Doctor testing scenario is not verified with non-admin user (`DOCTOR-80`_).

* Congress Nova driver is relying on deprecated Nova APIs and can lead to
  an error (`BUG#1670345`_). The workaround for this issue is to specify nova
  micro version to 2.34 . Apex is using this workaround for OpenStack Newton
  (`REVIEW#29463`_).

.. _DOCTOR-80: https://jira.opnfv.org/browse/DOCTOR-80
.. _BUG#1670345: https://bugs.launchpad.net/congress/+bug/1670345
.. _REVIEW#29463: https://gerrit.opnfv.org/gerrit/29463/
