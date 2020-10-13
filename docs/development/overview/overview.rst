.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Platform overview
"""""""""""""""""

Doctor platform provides these features since `Danube Release <https://wiki.opnfv.org/display/SWREL/Danube>`_:

* Immediate Notification
* Consistent resource state awareness for compute host down
* Valid compute host status given to VM owner

These features enable high availability of Network Services on top of
the virtualized infrastructure. Immediate notification allows VNF managers
(VNFM) to process recovery actions promptly once a failure has occurred.
Same framework can also be utilized to have VNFM awareness about
infrastructure maintenance.

Consistency of resource state is necessary to execute recovery actions
properly in the VIM.

Ability to query host status gives VM owner the possibility to get
consistent state information through an API in case of a compute host
fault.

The Doctor platform consists of the following components:

* OpenStack Compute (Nova)
* OpenStack Networking (Neutron)
* OpenStack Telemetry (Ceilometer)
* OpenStack Alarming (AODH)
* Doctor Sample Inspector, OpenStack Congress or OpenStack Vitrage
* Doctor Sample Monitor or any monitor supported by Congress or Vitrage

.. note::
    Doctor Sample Monitor is used in Doctor testing. However in real
    implementation like Vitrage, there are several other monitors supported.

You can see an overview of the Doctor platform and how components interact in
:numref:`figure-p1`.


Maintenance use case provides these features since `Iruya Release <https://wiki.opnfv.org/display/SWREL/Iruya>`_:

* Infrastructure maintenance and upgrade workflow
* Interaction between VNFM and infrastructe workflow

Since `Jerma Release <https://wiki.opnfv.org/display/SWREL/Jerma>`_ maintenance
use case also supports 'ETSI FEAT03' implementation to have the infrastructure
maintenance and upgrade fully optimized while keeping zero impact on VNF
service.

