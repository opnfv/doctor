.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

==========================
Inspector Design Guideline
==========================

.. NOTE::
   This is spec draft of design guideline for inspector component.
   JIRA ticket to track the update and collect comments: `DOCTOR-73`_.

This document summarize the best practise in designing a high performance
inspector to meet the requirements in `OPNFV Doctor project`_.

Problem Description
===================

Some pitfalls has be detected during the development of sample inspector, e.g.
we suffered a significant `performance degrading in listing VMs in a host`_.

A `patch set for caching the list`_ has been committed to solve issue. When a
new inspector is integrated, it would be nice to have an evaluation of existing
design and give recommendations for improvements.

This document can be treated as a source of related blueprints in inspector
projects.

Guidelines
==========

Host specific VMs list
----------------------

While requirement in doctor project is to have alarm about fault to consumer in one second, it is just a limit we have
set in requirements. When talking about fault management in Telco, the implementation needs to be by all means optimal
and the one second is far from traditional Telco requirements.

One thing to be optimized in inspector is to eliminate the need to read list of host specific VMs from Nova API, when
it gets a host specific failure event. Optimal way of implementation would be to initialize this list when Inspector
start by reading from Nova API and after this list would be kept up-to-date by ``instance.update`` notifications
received from nova. Polling Nova API can be used as a complementary channel to make snapshot of hosts and VMs list in
order to keep the data consistent with reality.

This is enhancement and not perhaps something needed to keep under one second in a small system. Anyhow this would be
something needed in case of production use.

This guideline can be summarized as following:

- cache the host VMs mapping instead of reading it on request
- subscribe and handle update notifications to keep the list up to date
- make snapshot periodically to ensure data consistency

Parallel execution
------------------

TBD, see `discussion in mailing list`_.

.. _DOCTOR-73: https://jira.opnfv.org/browse/DOCTOR-73
.. _OPNFV Doctor project: https://wiki.opnfv.org/doctor
.. _performance degrading in listing VMs in a host: https://lists.opnfv.org/pipermail/opnfv-tech-discuss/2016-September/012591.html
.. _patch set for caching the list: https://gerrit.opnfv.org/gerrit/#/c/20877/
.. _DOCTOR-76: https://jira.opnfv.org/browse/DOCTOR-76
.. _discussion in mailing list: https://lists.opnfv.org/pipermail/opnfv-tech-discuss/2016-October/013036.html
