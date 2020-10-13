.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Doctor Installation
====================

You can clone doctor project in OPNFV installer jumphost or if you are not
in OPNFV environment you can clone Doctor to DevStack controller node

git clone https://gerrit.opnfv.org/gerrit/doctor

In DevStack controller here is a sample of including what Doctor testing
will require for sample fault management testing and for maintenance
testing using Fenix

.. code-block:: bash

    git clone https://github.com/openstack/devstack -b stable/train

.. code-block:: bash

    cd devstack vi local.conf
    
.. code-block:: bash

    [[local|localrc]]
    GIT_BASE=https://git.openstack.org
    HOST_IP=<host_ip>
    ADMIN_PASSWORD=admin
    DATABASE_PASSWORD=admin
    RABBIT_PASSWORD=admin
    SERVICE_PASSWORD=admin
    LOGFILE=/opt/stack/stack.sh.log
    
    PUBLIC_INTERFACE=eth0
    
    CEILOMETER_EVENT_ALARM=True
    
    ENABLED_SERVICES=key,rabbit,mysql,fenix-engine,fenix-api,aodh-evaluator,aodh-notifier,aodh-api
    
    enable_plugin ceilometer https://git.openstack.org/openstack/ceilometer stable/train
    enable_plugin aodh https://git.openstack.org/openstack/aodh stable/train
    enable_plugin gnocchi https://github.com/openstack/gnocchi
    enable_plugin fenix https://opendev.org/x/fenix master
