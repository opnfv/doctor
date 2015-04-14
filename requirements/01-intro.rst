Introduction
============

The goal of this project is to build an NFVI fault management and maintenance
framework supporting high availability of the Network Services on top of the
virtualized infrastructure. The key feature is immediate notification of
unavailability of virtualized resources from VIM, to support failure recovery,
or failure avoidance of VNFs running on them. Requirement survey and development
of missing features in NFVI and VIM are in scope of this project in order to
fulfil requirements for fault management and maintenance in NFV.

The purpose of this requirement project is to clarify the necessary features of
NFVI fault management, and maintenance, identify missing features in the current
OpenSource implementations, provide a potential implementation architecture and
plan, provide implementation guidelines in relevant upstream projects to realize
those missing features, and define the VIM northbound interfaces necessary to
perform the task of NFVI fault management, and maintenance in alignment with
ETSI NFV [10]_.

Problem description
-------------------

A Virtualized Infrastructure Manager (VIM), e.g. OpenStack [3]_, cannot detect
certain Network Functions Virtualization Infrastructure (NFVI) faults. This
feature is necessary to detect the faults and notify the Consumer in order to
ensure the proper functioning of EPC VNFs like MME and S/P-GW.

* EPC VNFs are often in active standby (ACT-STBY) configuration and need to
  switch from STBY mode to ACT mode as soon as relevant faults are detected in
  the active (ACT) VNF.

* NFVI encompasses all elements building up the environment in which VNFs are
  deployed, e.g., Physical Machines, Hypervisors, Storage, and Network elements.

In addition, VIM, e.g. OpenStack, needs to receive maintenance instructions from
the Consumer, i.e. the operator/administrator of the VNF.

* Change the state of certain Physical Machines (PMs), e.g. empty the PM, so
  that maintenance work can be performed at these machines.

Note: Although fault management and maintenance are different operations in NFV,
both are considered as part of this project as -- except for the trigger -- they
share a very similar work and message flow. Hence, from implementation
perspective, these two are kept together in the Doctor project because of this
high degree of similarity.

..
 vim: set tabstop=4 expandtab textwidth=80:
