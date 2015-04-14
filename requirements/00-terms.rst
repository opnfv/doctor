Definition of terms
===================

Different SDOs and communities use different terminology related to
NFV/Cloud/SDN. This list tries to define an OPNFV terminology,
mapping/translating the OPNFV terms to terminology used in other contexts.

NFV
    Network Function Virtualization

NFVI
    Network Function Virtualization Infrastructure; totality of all hardware and
    software components which build up the environment in which VNFs are
    deployed.

VNF
    Virtualized Network Function. Implementation of an Network Function that can
    be deployed on a Network Function Virtualization Infrastructure (NFVI).

VIM
    Virtualized Infrastructure Manager; functional block that is responsible for
    controlling and managing the NFVI compute, storage and network resources,
    usually within one operator's Infrastructure Domain, e.g. NFVI Point of
    Presence (NFVI-PoP).

NFVO
    Network Functions Virtualization Orchestrator; functional block that manages
    the Network Service (NS) lifecycle and coordinates the management of NS
    lifecycle, VNF lifecycle (supported by the VNFM) and NFVI resources
    (supported by the VIM) to ensure an optimized allocation of the necessary
    resources and connectivity.

VNFM
    Virtualized Network Function Manager; functional block that is responsible
    for the lifecycle management of VNF.

Consumer
    User-side Manager; consumer of the interfaces produced by the VIM; VNFM,
    NFVO, or Orchestrator in ETSI NFV [11]_ terminology.

Administrator
    Administrator of the system, e.g. OAM in Telco context.

Virtual Machine (VM)
    Virtualized computation environment that behaves very much like a physical
    computer/server.

Virtual Storage
    Virtualized non-volatile storage allocated to a VM.

Virtual network
    Virtual network routes information among the network interfaces of VM
    instances and physical network interfaces, providing the necessary
    connectivity.

Physical resource
    Actual resources in NFVI; not visible to Consumer.

Virtual resource
    A Virtual Machine (VM), a virtual network, or virtualized storage; Offered
    resources to "Consumer" as result of infrastructure virtualization; visible
    to Consumer.

..
 vim: set tabstop=4 expandtab textwidth=80:
