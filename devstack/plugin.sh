#!/usr/bin/env bash

##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Defaults
# --------

CONF_FILES=(
    /etc/cinder/cinder.conf
    /etc/heat/heat.conf
    /etc/keystone/keystone.conf
    /etc/nova/nova.conf
    /etc/neutron/neutron.conf
    /etc/glance/glance-api.conf
    /etc/glance/glance-registry.conf
)

function install_doctor {
    # no-op
    :
}

function configure_doctor {
    for conf in ${CONF_FILES[@]}; do
        if [ -f $conf ]
        then
            iniset $conf profiler enabled true
            iniset $conf profiler trace_sqlalchemy true
            iniset $conf profiler hmac_keys ${OSPROFILER_HMAC_KEYS-doctor}
            iniset $conf profiler connection_string ${OSPROFILER_CONNECTION_STRING-redis://127.0.0.1:6379}
        fi
    done
}

function init_doctor {
    # no-op
    :
}

# check for service enabled
if is_service_enabled doctor; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring system services Doctor"
        # install_package cowsay

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing Doctor"
        install_doctor

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring Doctor"
        configure_doctor

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the doctor service
        echo_summary "Initializing Doctor"
        init_doctor
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down doctor services
        # no-op
        :
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi

