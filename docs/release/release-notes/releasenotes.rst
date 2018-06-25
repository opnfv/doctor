.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

===================================
OPNFV Doctor release notes (Fraser)
===================================

This document provides an overview of the Doctor project in the OPNFV Fraser
release, including new features, known issues and documentation updates.

Version history
===============

+------------+----------+--------------+-------------+
| **Date**   | **Ver.** | **Author**   | **Comment** |
+============+==========+==============+=============+
| 2018-06-25 | 6.2.0    | Tomi Juvonen |             |
| 2018-05-25 | 6.1.0    | Tomi Juvonen |             |
| 2018-04-23 | 6.0.0    | Tomi Juvonen |             |
+------------+----------+--------------+-------------+

Important notes
===============

OPNFV Doctor project started as a requirement project and identified gaps
between "as-is" open source software (OSS) and an "ideal" platform for NFV.
Based on this analysis, the Doctor project proposed missing features to
upstream OSS projects. After those features were implemented, OPNFV installer
projects integrated the features to the OPNFV platform and the OPNFV
infra/testing projects verified the functionalities in the OPNFV Labs. After
Euphrates release Doctor also graduated and became a mature project. This means
it has completed the implementation of the fault management use case. Based on
this implementation, Doctor has now started to implement the second use case on
maintenance.

For Fraser release, the Doctor project completed re-factoring testing code by
python, added support for installers and started working the maintenance use
case. Doctor now supports Apex, Fuel, Joid, Compass and Daisy installer.

New features
============

Doctor now supports Vitrage as Inspector for local installer.

Installer support and verification status
=========================================

Integrated features
-------------------

- The enhancement work for Doctor testing code done by re-factoring in python is
  now complete.
- Lint support for the code changes was added.
- Doctor now supports Vitrage as Inspector for local installer.

OPNFV installer support matrix
------------------------------

Doctor has already support for several installers for fault management testing.
This work also continued in the Fraser release. Here is latest additions [*]

+-----------+--------------+--------------+-----------------+--------------+--------------+
| Installer | Aodh         | Nova: Force  | Nova: Get valid | Congress     | Vitrage      |
|           | integration  | compute down | service status  | integration  | integration  |
+===========+==============+==============+=================+==============+==============+
| Apex      | Available    | Available    | Available       | Available    | N/A          |
+-----------+--------------+--------------+-----------------+--------------+--------------+
| Fuel      | Available    | Available    | Available       | TBC          | N/A          |
| (MCP)     |              |              |                 |              |              |
+-----------+--------------+--------------+-----------------+--------------+--------------+
| Joid      | Available    | TBC          | TBC             | Available    | N/A          |
|           | Not verified |              |                 | Not verified |              |
+-----------+--------------+--------------+-----------------+--------------+--------------+
| Compass   | Available    | TBC          | TBC             | Available    | N/A          |
|           | Not verified |              |                 | Not verified |              |
+-----------+--------------+--------------+-----------------+--------------+--------------+
| Daisy*    | Available    | TBC          | TBC             | TBC          | N/A          |
|           |              |              |                 |              |              |
+-----------+--------------+--------------+-----------------+--------------+--------------+
| Local     | Available    | TBC          | TBC             | Available    | Available*   |
|           | Not verified |              |                 | Not verified | Not verified |
+-----------+--------------+--------------+-----------------+--------------+--------------+

Note: Local installer is devstack.

Note: 'Not verified' means that we didn't verify the functionality by having
our own test scenario running in OPNFV CI pipeline yet.

Documentation updates
=====================

No major updates

Known issues
============

- Testing code for `port-data-plane-status` in Doctor repository was disabled
  in 5.0, as we have problem in neutron client load in CI job container.
- Maintenance test case work was started in Fraser. Some initial test case code
  is available, however it is yet not fully implemented in this release.
