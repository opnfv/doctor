.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Doctor platform components and features
=======================================

..
    This section will be compiled into OPNFV composite document.

https://wiki.opnfv.org/doctor

Features
--------

Doctor platform provides these features in `Colorado Release <https://wiki.opnfv.org/display/SWREL/Colorado>`_:

* Immediate Notification
* Consistent resource state awareness for compute host down
* Valid compute host status given to VM owner

These features enable high availability of Network Services on top of
the virtualized infrastructure.

Immediate notification allows VNF managers (VNFM) to process recovery
actions promptly once a failure has occurred.

Consistency of resource state is necessary to properly execute recovery
actions properly in the VIM.

Ability to query host status gives VM owner (VNFM) the possibility to get
consistent state information through an API in case of a compute host
fault.

Components
----------

Doctor platform, as of Colorado release, consists of the following
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

.. figure:: /docs/platformoverview/images/figure-p1.png
    :name: figure-p1
    :width: 100%

    Doctor platform and typical sequence (Colorado)

Detailed information on the Doctor architecture can be found in the Doctor
requirements documentation:
http://artifacts.opnfv.org/doctor/docs/requirements/05-implementation.html
