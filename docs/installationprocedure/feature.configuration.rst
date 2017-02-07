.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Doctor Configuration
====================

OPNFV installers install most components of Doctor framework including
OpenStack Nova, Neutron and Cinder (Doctor Controller) and OpenStack
Ceilometer and Aodh (Doctor Notifier) except Doctor Monitor.

After major components of OPNFV are deployed, you can setup Doctor functions
by following instructions in this section. You can also learn detailed
steps in setup_installer() under `doctor/tests`_.

.. _doctor/tests: https://gerrit.opnfv.org/gerrit/gitweb?p=doctor.git;a=tree;f=tests;

Doctor Inspector
----------------

You need to configure one of Doctor Inspector below.

**Doctor Sample Inspector**

Sample Inspector is intended to show minimum functions of Doctor Inspector.

Doctor Sample Inspector suggested to be placed in one of the controller nodes,
but it can be put on any host where Doctor Monitor can reach and access
the OpenStack Controller (Nova).

Make sure OpenStack env parameters are set properly, so that Doctor Inspector
can issue admin actions such as compute host force-down and state update of VM.

Then, you can configure Doctor Inspector as follows:

.. code-block:: bash

    git clone https://gerrit.opnfv.org/gerrit/doctor -b stable/danube
    cd doctor/tests
    INSPECTOR_PORT=12345
    python inspector.py $INSPECTOR_PORT > inspector.log 2>&1 &

**Congress**

OpenStack `Congress`_ is a Governance as a Service (previously Policy as a
Service). Congress implements Doctor Inspector as it can inspect a fault
situation and propagate errors onto other entities.

.. _Congress: https://wiki.openstack.org/wiki/Congress

Congress is deployed by OPNFV installers. You need to enable doctor
datasource driver and set policy rules. By the example configuration below,
Congress will force down nova compute service when it received a fault event
of that compute host. Also, Congress will set the state of all VMs running on
that host from ACTIVE to ERROR state.

.. code-block:: bash

    openstack congress datasource create doctor doctor

    openstack congress policy rule create \
        --name host_down classification \
        'host_down(host) :-
            doctor:events(hostname=host, type="compute.host.down", status="down")'

    openstack congress policy rule create \
        --name active_instance_in_host classification \
        'active_instance_in_host(vmid, host) :-
            nova:servers(id=vmid, host_name=host, status="ACTIVE")'

    openstack congress policy rule create \
        --name host_force_down classification \
        'execute[nova:services.force_down(host, "nova-compute", "True")] :-
            host_down(host)'

    openstack congress policy rule create \
        --name error_vm_states classification \
        'execute[nova:servers.reset_state(vmid, "error")] :-
            host_down(host),
            active_instance_in_host(vmid, host)'

Doctor Monitor
--------------

**Doctor Sample Monitor**

Doctor Monitors are suggested to be placed in one of the controller nodes,
but those can be put on any host which is reachable to target compute host and
accessible by the Doctor Inspector.
You need to configure Monitors for all compute hosts one by one.

Make sure OpenStack env parameters are set properly, so that Doctor Inspector
can issue admin actions such as compute host force-down and state update of VM.

Then, you can configure the Doctor Monitor as follows (Example for Apex deployment):

.. code-block:: bash

    git clone https://gerrit.opnfv.org/gerrit/doctor -b stable/danube
    cd doctor/tests
    INSPECTOR_PORT=12345
    COMPUTE_HOST='overcloud-novacompute-1.localdomain.com'
    COMPUTE_IP=192.30.9.5
    sudo python monitor.py "$COMPUTE_HOST" "$COMPUTE_IP" \
        "http://127.0.0.1:$INSPECTOR_PORT/events" > monitor.log 2>&1 &
