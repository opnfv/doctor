.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Summary and conclusion
======================

The Doctor project aimed at detailing NFVI fault management and NFVI maintenance
requirements. These are indispensable operations for an Operator, and extremely
necessary to realize telco-grade high availability. High availability is a large
topic; the objective of Doctor is not to realize a complete high availability
architecture and implementation. Instead, Doctor limited itself to addressing
the fault events in NFVI, and proposes enhancements necessary in VIM, e.g.
OpenStack, to ensure VNFs availability in such fault events, taking a Telco VNFs
application level management system into account.

The Doctor project performed a robust analysis of the requirements from NFVI
fault management and NFVI maintenance operation, concretely found out gaps in
between such requirements and the current implementation of OpenStack.
A detailed architecture and interface specification has been described in this
document and work to realize Doctor features and fill out the identified gaps
in upstream communities is in the final stages of development.
