.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

==============
Testing Doctor
==============

You have two options to test Doctor functions automatically.

Run Test Script
===============

Doctor project has own testing script under `doctor/tests`_.

.. _doctor/tests: https://gerrit.opnfv.org/gerrit/gitweb?p=doctor.git;a=tree;f=tests;

Before running this script, you need to install OpenStack and other OPNFV
components except Doctor Sample Inspector and Sample Monitor, as these will be
launched in this script. And, make sure OpenStack env parameters are set
properly, so that Doctor Inspector can operate OpenStack services.

Then, you can run the script as follows:

.. code-block:: bash

    git clone https://gerrit.opnfv.org/gerrit/doctor -b stable/danube
    cd doctor/tests
    export INSPECTOR_TYPE=sample
    ./run.sh

INSPECTOR_TYPE can be specified eigther 'sample' or 'congress'.

Run Functest Suite
==================

Functest supports Doctor testing by triggering the test script above.
You can run the Doctor test by using Functest container with the following
steps:

.. code-block:: bash

    docker pull opnfv/functest:stable
    docker run --privileged=true -id \
        -e INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP} \
        -e INSPECTOR_TYPE=sample -v /root/.ssh/id_rsa:/root/.ssh/id_rsa \
        opnfv/functest:stable /bin/bash
    docker exec <container_id> python /home/opnfv/repos/functest/functest/ci/prepare_env.py start
    docker exec <container_id> functest testcase run doctor

See `Functest Userguide`_.

.. _Functest Userguide: http://artifacts.opnfv.org/functest/docs/userguide/index.html

Tips
====
