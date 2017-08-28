##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import itertools

from oslo_config import cfg

import alarm
import consumer
import image
import instance
import installer
import network
import inspector
import monitor
import os_clients
import profiler_poc
import user


def list_opts():
    return [
        ('installer', installer.OPTS),
        ('monitor', monitor.OPTS),
        ('inspector', inspector.OPTS),
        ('consumer', consumer.OPTS),
        ('DEFAULT', itertools.chain(
            os_clients.OPTS,
            image.OPTS,
            user.OPTS,
            network.OPTS,
            instance.OPTS,
            alarm.OPTS,
            profiler_poc.OPTS]))
    ]


def prepare_conf(args=None, conf=None, config_files=None):
    if conf is None:
        conf = cfg.ConfigOpts()

    for group, options in list_opts():
        conf.register_opts(list(options),
                           group=None if group == 'DEFAULT' else group)

    conf(args, project='doctor', validate_default_values=True,
         default_config_files=config_files)

    return conf
