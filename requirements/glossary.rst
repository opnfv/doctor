**Definition of terms**

Different SDOs and communities use different terminology related to
NFV/Cloud/SDN. This list tries to define an OPNFV terminology,
mapping/translating the OPNFV terms to terminology used in other contexts.


.. glossary::

    ACT-STBY configuration
        Failover configuration common in Telco deployments. It enables the
        operator to use a standby (STBY) instance to take over the functionality
        of a failed active (ACT) instance.

    Administrator
        Administrator of the system, e.g. OAM in Telco context.

    Consumer
        User-side Manager; consumer of the interfaces produced by the VIM; VNFM,
        NFVO, or Orchestrator in ETSI NFV [11]_ terminology.

    EPC
        Evolved Packet Core, the main component of the core network architecture
        of 3GPP's LTE communication standard.

    MME
        Mobility Management Entity, an entity in the EPC dedicated to mobility
        management.

    NFV
        Network Function Virtualization

    NFVI
        Network Function Virtualization Infrastructure; totality of all hardware
        and software components which build up the environment in which VNFs are
        deployed.

    S/P-GW
        Serving/PDN-Gateway, two entities in the EPC dedicated to routing user
        data packets and providing connectivity from the UE to external packet
        data networks (PDN), respectively.

    Physical resource
        Actual resources in NFVI; not visible to Consumer.

    VNFM
        Virtualized Network Function Manager; functional block that is
        responsible for the lifecycle management of VNF.

    NFVO
        Network Functions Virtualization Orchestrator; functional block that
        manages the Network Service (NS) lifecycle and coordinates the
        management of NS lifecycle, VNF lifecycle (supported by the VNFM) and
        NFVI resources (supported by the VIM) to ensure an optimized allocation
        of the necessary resources and connectivity.

    VIM
        Virtualized Infrastructure Manager; functional block that is responsible
        for controlling and managing the NFVI compute, storage and network
        resources, usually within one operator's Infrastructure Domain, e.g.
        NFVI Point of Presence (NFVI-PoP).

    Virtual Machine (VM)
        Virtualized computation environment that behaves very much like a
        physical computer/server.

    Virtual network
        Virtual network routes information among the network interfaces of VM
        instances and physical network interfaces, providing the necessary
        connectivity.

    Virtual resource
        A Virtual Machine (VM), a virtual network, or virtualized storage;
        Offered resources to "Consumer" as result of infrastructure
        virtualization; visible to Consumer.

    Virtual Storage
        Virtualized non-volatile storage allocated to a VM.

    VNF
        Virtualized Network Function. Implementation of an Network Function that
        can be deployed on a Network Function Virtualization Infrastructure
        (NFVI).

..
 vim: set tabstop=4 expandtab textwidth=80:
