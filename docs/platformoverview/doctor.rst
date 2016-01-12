===============
Doctor Platform
===============

https://wiki.opnfv.org/doctor

Features
========

Doctor platform, as of Brahmaputra release, provides the two features:

* Immediate Notification
* Consistent resource state awareness (Compute)

These features enable high availability of Network Services on top of
the virtualized infrastructure. Immediate notification allows VNF managers
(VNFM) to process recovery actions promptly once a failure has occurred.
Consistency of resource state is necessary to properly execute recovery
actions properly in the VIM.

Components
==========

Doctor platform, as of Brahmaputra release, consists of the following
components:

* OpenStack Compute (Nova)
* OpenStack Telemetry (Ceilometer)
* OpenStack Alarming (Aodh)
* Doctor Inspector
* Doctor Monitor

.. note::
    Doctor Inspector and Monitor are sample implementation for reference.

You can see an overview of the Doctor platform and how components interact in
:numref:`figure-p1`.

.. figure:: images/figure-p1.png
    :name: figure-p1
    :width: 100%

    Doctor platform and typical sequence (Brahmaputra)

Detailed information on the Doctor architecture can be found in the Doctor
requirements documentation:
http://artifacts.opnfv.org/doctor/docs/requirements/05-implementation.html
