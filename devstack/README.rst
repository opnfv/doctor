.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) 2017 OPNFV.

====================================
Enabling OPNFV Doctor using DevStack
====================================

This directory contains the files necessary to run OpenStack with enabled
OPNFV Doctor in DevStack.

1. To configure DevStack to enable OPNFV Doctor edit
``${DEVSTACK_DIR}/local.conf`` file and add::

    enable_plugin aodh http://git.openstack.org/openstack/aodh
    enable_plugin panko https://git.openstack.org/openstack/panko
    enable_plugin ceilometer https://git.openstack.org/openstack/ceilometer
    enable_plugin osprofiler https://git.openstack.org/openstack/osprofiler
    enable_plugin doctor https://git.opnfv.org/doctor

to the ``[[local|localrc]]`` section. Or, you can copy the local.conf.sample::

    cp /<path-to-doctor>/devstack/local.conf.sample ${DEVSTACK_DIR}/local.conf

.. note:: The order of enabling plugins matters.

2. To enable Python 3 in DevStack, please add::

   USE_PYTHON3=True

3. To enable Congress as Doctor Inspector, please add::

   enable_plugin congress https://git.openstack.org/openstack/congress

4. To enable Neutron port data plane status, please also add::

   Q_ML2_PLUGIN_EXT_DRIVERS=data_plane_status

5. Run DevStack as normal::

    $ ./stack.sh
