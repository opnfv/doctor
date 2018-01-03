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

from doctor_tests import alarm
from doctor_tests import consumer
from doctor_tests import image
from doctor_tests import instance
from doctor_tests import installer
from doctor_tests import network
from doctor_tests import inspector
from doctor_tests import monitor
from doctor_tests import os_clients
from doctor_tests import profiler_poc
from doctor_tests import user
from doctor_tests.scenario import maintenance


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
            profiler_poc.OPTS,
            maintenance.OPTS))
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
