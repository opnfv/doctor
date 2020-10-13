.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

==============
Testing Doctor
==============

You have two options to test Doctor functions with the script developed
for doctor CI.

You need to install OpenStack and other OPNFV components except Doctor Sample
Inspector, Sample Monitor and Sample Consumer, as these will be launched in
this script. You are encouraged to use OPNFV official installers, but you can
also deploy all components with other installers such as devstack or manual
operation. In those cases, the versions of all components shall be matched with
the versions of them in OPNFV specific release.

Run Test Script
===============

Doctor project has own testing script under `doctor/doctor_tests`_. This test script
can be used for functional testing agained an OPNFV deployment.

.. _doctor/doctor_tests: https://git.opnfv.org/doctor/tree/doctor_tests

Before running this script, make sure OpenStack env parameters are set properly
(See e.g. `OpenStackClient Configuration`_), so that Doctor Inspector can operate
OpenStack services.

.. _OpenStackClient Configuration: https://docs.openstack.org/python-openstackclient/latest/configuration/index.html

Doctor now supports different test cases and for that you might want to
export TEST_CASE with different values:

.. code-block:: bash

    #Fault management (default)
    export TEST_CASE='fault_management'
    #Maintenance (requires 3 compute nodes)
    export TEST_CASE='maintenance'
    #Run both tests cases
    export TEST_CASE='all'

    #Use Fenix in maintenance testing instead of sample admin_tool
    #This is only for 'mainteanance' test case
    export ADMIN_TOOL_TYPE='fenix'
    export APP_MANAGER_TYPE='vnfm'

    #Run in different installer jumphost 'fuel' or 'apex'
    #In multinode DevStack you run Doctor in controller node
    #with value export APP_MANAGER_TYPE=vnfm
    export INSTALLER_TYPE='fuel'

Run Python Test Script
~~~~~~~~~~~~~~~~~~~~~~

You can run the python script as follows:

.. code-block:: bash

    git clone https://gerrit.opnfv.org/gerrit/doctor
    cd doctor && tox

You can see all the configurations with default values in sample configuration
file `doctor.sample.conf`_. And you can also modify the file to meet your
environment and then run the test.

.. _doctor.sample.conf: https://git.opnfv.org/doctor/tree/etc/doctor.sample.conf

In OPNFV testing environment jumphost you can run Doctor testing as follows
using tox:

.. code-block:: bash

    source overcloudrc
    export INSTALLER_IP=${INSTALLER_IP}
    export INSTALLER_TYPE=${INSTALLER_TYPE}
    git clone https://gerrit.opnfv.org/gerrit/doctor
    cd doctor
    sudo -E tox
    
Note! In DevStack you run Doctor in controller node.
