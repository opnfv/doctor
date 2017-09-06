.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

==============
Testing Doctor
==============

You have two options to test Doctor functions with the script developed
for doctor CI.

You need to install OpenStack and other OPNFV components except Doctor Sample
Inspector, Sample Monitor and Sample Consumer, as these will be launched in
this script. You are encouraged to use OPNFV offcial installers, but you can
also deploy all components with other installers such as devstack or manual
operation. In those cases, the versions of all components shall be matched with
the versions of them in OPNFV specific release.

Run Test Script
===============

Doctor project has own testing script under `doctor/tests`_. This test script
can be used for functional testing agained an OPNFV deployment.

.. _doctor/tests: https://gerrit.opnfv.org/gerrit/gitweb?p=doctor.git;a=tree;f=tests;

Before running this script, make sure OpenStack env parameters are set properly
following `OpenStack CLI manual`_, so that Doctor Inspector can operate
OpenStack services.

.. _OpenStack CLI manual: https://docs.openstack.org/user-guide/common/cli-set-environment-variables-using-openstack-rc.html

Run Bash Test Script
~~~~~~~~~~~~~~~~~~~~

You can run the bash script as follows:

.. code-block:: bash

    git clone https://gerrit.opnfv.org/gerrit/doctor
    cd doctor/tests
    export INSTALLER_TYPE=local
    export INSPECTOR_TYPE=sample
    ./run.sh

INSTALLER_TYPE can be 'apex', 'fuel', 'joid' and 'local'(default). If you are
not using OPNFV installers in this option, chose 'local'.
INSPECTOR_TYPE can be specified either 'sample'(default) or 'congress'.

For testing with stable version, checkout stable branch of doctor repo before
'./run.sh'.

The bash test script will be deprecated(only bug fixes) after E Release.

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

Run Functest Suite
==================

Functest supports Doctor testing by triggering the test script above in a
Functest container. You can run the Doctor test with the following steps:

.. code-block:: bash

    DOCKER_TAG=latest
    docker pull opnfv/functest:${DOCKER_TAG}
    docker run --privileged=true -id \
        -e INSTALLER_TYPE=${INSTALLER_TYPE} \
        -e INSTALLER_IP=${INSTALLER_IP} \
        -e INSPECTOR_TYPE=sample \
        -e PYTHON_ENABLE=True \
        opnfv/functest:${DOCKER_TAG} /bin/bash
    docker exec <container_id> python /home/opnfv/repos/functest/functest/ci/prepare_env.py start
    docker exec <container_id> functest testcase run doctor

Add an environment variable *PYTHON_ENABLE* to indicate that using Python or
Bash to run the test when start the docker container.

See `Functest Userguide`_ for more information.

.. _Functest Userguide: http://artifacts.opnfv.org/functest/docs/userguide/index.html

For testing with stable version, change DOCKER_TAG to 'stable' or other release
tag identifier.

Tips
====
