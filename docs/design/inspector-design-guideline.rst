.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

==========================
Inspector Design Guideline
==========================

.. NOTE::
   This is spec draft of design guideline for inspector component.
   JIRA ticket to track the update and collect comments: DOCTOR-73 [1_].

This document summarize the best practise in designing a high performance
inspector to meet the requirements in OPNFV Doctor project [2_].

Problem Description
===================

Some pitfalls[3_] has be detected during the development of sample inspector, e.g.
we suffered a significant performance degrading in listing VMs in a host.

A patch set [4_] for caching the list has been committed to solve issue. When a
new inspector is integrated, it would be nice to have an evaluation of current
design and give recommendations for improvements.

This document can be treated as a source of related blueprints in inspector
projects.

References
==========

.. [1] DOCTOR-73: Inspector design guideline,
   https://jira.opnfv.org/browse/DOCTOR-73
.. [2] OPNFV Doctor project,
   https://wiki.opnfv.org/doctor
.. [3] For the issue about the notification time is large than 1S,
   https://lists.opnfv.org/pipermail/opnfv-tech-discuss/2016-September/012591.html
.. [4] cache host-vm list when inspect start to run,
   https://gerrit.opnfv.org/gerrit/#/c/20877/

