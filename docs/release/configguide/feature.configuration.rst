.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Doctor Configuration
====================

OPNFV installers install most components of Doctor framework including
OpenStack Nova, Neutron and Cinder (Doctor Controller) and OpenStack
Ceilometer and Aodh (Doctor Notifier) except Doctor Monitor.

After major components of OPNFV are deployed, you can setup Doctor functions
by following instructions in this section. You can also learn detailed
steps for all supported installers under `doctor/doctor_tests/installer`_.

.. _doctor/doctor_tests/installer: https://git.opnfv.org/doctor/tree/doctor_tests/installer

Doctor Inspector
----------------

You need to configure one of Doctor Inspectors below. You can also learn detailed steps for
all supported Inspectors under `doctor/doctor_tests/inspector`_.

.. _doctor/doctor_tests/inspector: https://git.opnfv.org/doctor/tree/doctor_tests/inspector


**Sample Inspector**

Sample Inspector is intended to show minimum functions of Doctor Inspector.

Sample Inspector is suggested to be placed in one of the controller nodes,
but it can be put on any host where Sample Inspector can reach and access
the OpenStack Controllers (e.g. Nova, Neutron).

Make sure OpenStack env parameters are set properly, so that Sample Inspector
can issue admin actions such as compute host force-down and state update of VM.

Then, you can configure Sample Inspector as follows:

.. code-block:: bash

    git clone https://gerrit.opnfv.org/gerrit/doctor
    cd doctor/doctor_tests/inspector
    INSPECTOR_PORT=12345
    python sample.py $INSPECTOR_PORT > inspector.log 2>&1 &

**Congress**

OpenStack `Congress`_ is a Governance as a Service (previously Policy as a
Service). Congress implements Doctor Inspector as it can inspect a fault
situation and propagate errors onto other entities.

.. _Congress: https://governance.openstack.org/tc/reference/projects/congress.html

Congress is deployed by OPNFV Apex installer. You need to enable doctor
datasource driver and set policy rules. By the example configuration below,
Congress will force down nova compute service when it received a fault event
of that compute host. Also, Congress will set the state of all VMs running on
that host from ACTIVE to ERROR state.

.. code-block:: bash

    openstack congress datasource create doctor "doctor"

    openstack congress datasource create --config api_version=$NOVA_MICRO_VERSION \
        --config username=$OS_USERNAME --config tenant_name=$OS_TENANT_NAME \
        --config password=$OS_PASSWORD --config auth_url=$OS_AUTH_URL \
        nova "nova21"

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

**Vitrage**

OpenStack `Vitrage`_ is an RCA (Root Cause Analysis) service for organizing,
analyzing and expanding OpenStack alarms & events. Vitrage implements Doctor
Inspector, as it receives a notification that a host is down and calls Nova
force-down API. In addition, it raises alarms on the instances running on this
host.

.. _Vitrage: https://wiki.openstack.org/wiki/Vitrage

Vitrage is not deployed by OPNFV installers yet. It can be installed either on
top of a devstack environment, or on top of a real OpenStack environment. See
`Vitrage Installation`_

.. _`Vitrage Installation`: https://docs.openstack.org/developer/vitrage/installation-and-configuration.html

Doctor SB API and a Doctor datasource were implemented in Vitrage in the Ocata
release. The Doctor datasource is enabled by default.

After Vitrage is installed and configured, there is a need to configure it to
support the Doctor use case. This can be done in a few steps:

1. Make sure that 'aodh' and 'doctor' are included in the list of datasource
   types in /etc/vitrage/vitrage.conf:

.. code-block:: bash

    [datasources]
    types = aodh,doctor,nova.host,nova.instance,nova.zone,static,cinder.volume,neutron.network,neutron.port,heat.stack

2. Enable the Vitrage Nova notifier. Set the following line in
   /etc/vitrage/vitrage.conf:

.. code-block:: bash

    [DEFAULT]
    notifiers = nova

3. Add a template that is responsible to call Nova force-down if Vitrage
   receives a 'compute.host.down' alarm. Copy `template`_ and place it under
   /etc/vitrage/templates

.. _template: https://github.com/openstack/vitrage/blob/master/etc/vitrage/templates.sample/host_down_scenarios.yaml

4. Restart the vitrage-graph and vitrage-notifier services


Doctor Monitors
---------------

Doctor Monitors are suggested to be placed in one of the controller nodes,
but those can be put on any host which is reachable to target compute host and
accessible by the Doctor Inspector.
You need to configure Monitors for all compute hosts one by one. You can also learn detailed
steps for all supported monitors under `doctor/doctor_tests/monitor`_.

.. _doctor/doctor_tests/monitor: https://git.opnfv.org/doctor/tree/doctor_tests/monitor

**Sample Monitor**
You can configure the Sample Monitor as follows (Example for Apex deployment):

.. code-block:: bash

    git clone https://gerrit.opnfv.org/gerrit/doctor
    cd doctor/doctor_tests/monitor
    INSPECTOR_PORT=12345
    COMPUTE_HOST='overcloud-novacompute-1.localdomain.com'
    COMPUTE_IP=192.30.9.5
    sudo python sample.py "$COMPUTE_HOST" "$COMPUTE_IP" \
        "http://127.0.0.1:$INSPECTOR_PORT/events" > monitor.log 2>&1 &

**Collectd Monitor**

OpenStack components
====================

In OPNFV and with Doctor testing you can have all OpenStack components configured
as needed. Here is sample of the needed configuration modifications.

Ceilometer
----------

/etc/ceilometer/event_definitions.yaml:
# Maintenance use case needs new alarm definitions to be added
- event_type: maintenance.scheduled
    traits:
      actions_at:
        fields: payload.maintenance_at
        type: datetime
      allowed_actions:
        fields: payload.allowed_actions
      host_id:
        fields: payload.host_id
      instances:
        fields: payload.instances
      metadata:
        fields: payload.metadata
      project_id:
        fields: payload.project_id
      reply_url:
        fields: payload.reply_url
      session_id:
        fields: payload.session_id
      state:
        fields: payload.state
- event_type: maintenance.host
    traits:
      host:
        fields: payload.host
      project_id:
        fields: payload.project_id
      session_id:
        fields: payload.session_id
      state:
        fields: payload.state

/etc/ceilometer/event_pipeline.yaml:
# Maintenance and Fault management both needs these to be added
    - notifier://
    - notifier://?topic=alarm.all

Nova
----

/etc/nova/nova.conf
cpu_allocation_ratio=1.0
