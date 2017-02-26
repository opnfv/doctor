##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from oslo_config import cfg

import opts


def prepare_service(args=None, conf=None, config_files=None):
    if conf is None:
        conf = cfg.ConfigOpts()

    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == 'DEFAULT' else group)

    return conf
