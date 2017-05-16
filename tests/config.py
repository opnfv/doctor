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
import network
import os_clients
import user


def list_opts():
    return [
        ('consumer', consumer.OPTS),
        ('DEFAULT', itertools.chain(
            os_clients.OPTS,
            image.OPTS,
            user.OPTS,
            network.OPTS,
            instance.OPTS,
            alarm.OPTS))
    ]


def prepare_conf(conf=None):
    if conf is None:
        conf = cfg.ConfigOpts()

    for group, options in list_opts():
        conf.register_opts(list(options),
                           group=None if group == 'DEFAULT' else group)

    return conf
