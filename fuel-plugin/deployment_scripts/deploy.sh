#!/bin/bash

# Fuel Plugin - OPNFV Fault Managment (Doctor)
#
# https://wiki.opnfv.org/display/doctor
#
# Version 9.0

CEILOMETER_CONF_DIR=/etc/ceilometer


if [ -e $CEILOMETER_CONF_DIR/event_pipeline.yaml ]; then
    if ! grep -q '^ *- notifier://?topic=alarm.all$' $CEILOMETER_CONF_DIR/event_pipeline.yaml; then
        sed -i 's|- notifier://|- notifier://?topic=alarm.all|' $CEILOMETER_CONF_DIR/event_pipeline.yaml
    fi

    service ceilometer-agent-notification restart
else
    echo "doctor failed: ceilometer file is not exist"
    exit 1
fi

exit 0
