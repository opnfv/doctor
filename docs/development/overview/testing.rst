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
    #Use Fenix in maintenance testing instead of sample admin_tool
    export TADMIN_TOOL_TYPE='fenix'
    #Run both tests cases
    export TEST_CASE='all'

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

In OPNFV Apex jumphost you can run Doctor testing as follows using tox:

.. code-block:: bash

    source overcloudrc
    export INSTALLER_IP=${INSTALLER_IP}
    export INSTALLER_TYPE=${INSTALLER_TYPE}
    git clone https://gerrit.opnfv.org/gerrit/doctor
    cd doctor
    sudo -E tox

Run Functest Suite
==================

Functest supports Doctor testing by triggering the test script above in a
Functest container. You can run the Doctor test with the following steps:

.. code-block:: bash

    DOCKER_TAG=latest
    docker pull docker.io/opnfv/functest-features:${DOCKER_TAG}
    docker run --privileged=true -id \
        -e INSTALLER_TYPE=${INSTALLER_TYPE} \
        -e INSTALLER_IP=${INSTALLER_IP} \
        -e INSPECTOR_TYPE=sample \
        docker.io/opnfv/functest-features:${DOCKER_TAG} /bin/bash
    docker exec <container_id> functest testcase run doctor-notification

See `Functest Userguide`_ for more information.

.. _Functest Userguide: :doc:`<functest:testing/user/userguide>`


For testing with stable version, change DOCKER_TAG to 'stable' or other release
tag identifier.

Tips
====
