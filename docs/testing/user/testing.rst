.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Run Functest Suite (obsolete)
=============================

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
