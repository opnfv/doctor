##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from oslo_config import cfg

from doctor import opts
from doctor.clients import register_keystoneauth_opts
from keystoneauth1 import loading as ka_loading

import logging

LOG = logging.getLogger("test")


OPTS = [
    cfg.StrOpt('aodh_version', default='2', help='Aodh version'),
    cfg.FloatOpt('nova_version', default='2.11', help='Nova version'),
    cfg.StrOpt('cinder_version', default='2', help='Cinder version'),
    cfg.StrOpt('heat_version', default='1', help='Heat version'),
]

def prepare_service(args=None, conf=None, config_files=None):
    if conf is None:
        conf = cfg.ConfigOpts()

    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == 'DEFAULT' else group)

    register_keystoneauth_opts(conf)

    # ka_loading.load_auth_from_conf_options(conf, 'keystone_authtoken')

    return conf
