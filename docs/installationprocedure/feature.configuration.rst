.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Doctor Configuration
====================

Doctor Inspector
----------------

Doctor Inspector is suggested to be placed in one of the controller nodes,
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

Doctor Monitor
--------------

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
