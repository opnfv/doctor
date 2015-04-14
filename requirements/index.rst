..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

.. title::
    Doctor

****************************************
Doctor: Fault Management and Maintenance
****************************************

:Project: Doctor, https://wiki.opnfv.org/doctor
:Editors: Ashiq Khan (NTT DOCOMO), Gerald Kunzmann (NTT DOCOMO)
:Authors: Ryota Mibu (NEC), Carlos Goncalves (NEC), Tomi Juvonen (Nokia),
          Tommy Lindgren (Ericsson)
:Project creation date: 2014-12-02
:Submission date: 2015-03-XX

:Abstract: Doctor is an OPNFV requirement project [1]_. Its scope is NFVI fault
           management, and maintenance and it aims at developing and realizing
           the consequent implementation for the OPNFV reference platform.

           This deliverable is introducing the use cases and operational
           scenarios for Fault Management considered in the Doctor project. From
           the general features, a high level architecture describing logical
           building blocks and interfaces is derived. Finally, a detailed
           implementation is introduced, based on available open source
           components, and a related gap analysis is done as part of this
           project. The implementation plan finally discusses an initial
           realization for a NFVI fault management and maintenance solution in
           open source software.


.. raw:: latex

    \newpage

.. include::
    glossary.rst

.. toctree::
    :maxdepth: 4
    :numbered:

    01-intro.rst
    02-use_cases.rst
    03-architecture.rst
    04-gaps.rst
    05-implementation.rst
    06-summary.rst

..

References and bibliography
===========================

[1] OPNFV, "Doctor" requirements project, [Online]. Available at
    https://wiki.opnfv.org/doctor

[2] OPNFV, "Data Collection for Failure Prediction" requirements project
    [Online]. Available at https://wiki.opnfv.org/prediction

[3] OpenStack, [Online]. Available at https://www.openstack.org/

[4] OpenStack Telemetry (Ceilometer), [Online]. Available at
    https://wiki.openstack.org/wiki/Ceilometer

[5] OpenStack Nova, [Online]. Available at
    https://wiki.openstack.org/wiki/Nova

[6] OpenStack Neutron, [Online]. Available at
    https://wiki.openstack.org/wiki/Neutron

[7] OpenStack Cinder, [Online]. Available at
    https://wiki.openstack.org/wiki/Cinder

[8] OpenStack Monasca, [Online], Available at
    https://wiki.openstack.org/wiki/Monasca

[9] OpenStack Cloud Administrator Guide, [Online]. Available at
    http://docs.openstack.org/admin-guide-cloud/content/

[10] ZABBIX, the Enterprise-class Monitoring Solution for Everyone, [Online].
     Available at http://www.zabbix.com/

[11] ETSI NFV, [Online]. Available at
     http://www.etsi.org/technologies-clusters/technologies/nfv


..
 vim: set tabstop=4 expandtab textwidth=80:
