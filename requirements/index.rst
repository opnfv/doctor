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

:Abstract: Doctor is an OPNFV requirement project [DOCT]_. Its scope is NFVI
           fault management, and maintenance and it aims at developing and
           realizing the consequent implementation for the OPNFV reference
           platform.

           This deliverable is introducing the use cases and operational
           scenarios for Fault Management considered in the Doctor project.
           From the general features, a high level architecture describing
           logical building blocks and interfaces is derived. Finally,
           a detailed implementation is introduced, based on available open
           source components, and a related gap analysis is done as part of
           this project. The implementation plan finally discusses an initial
           realization for a NFVI fault management and maintenance solution in
           open source software.

:History:

          ========== =====================================================
          Date       Description
          ========== =====================================================
          02.12.2014 Project creation
          14.04.2015 Initial version of the deliverable uploaded to Gerrit
          18.05.2015 Stable version of the Doctor deliverable
          ========== =====================================================


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
    07-annex.rst

.. include::
    99-references.rst


..
 vim: set tabstop=4 expandtab textwidth=80:
