##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from oslo_config import cfg

from doctor.doctor_test_refactor import opts


OPTS = [
    cfg.StrOpt('DOCTOR_USER',               default='doctor',
               help='openstack user fr OpenStack service access',
               required=True),
    cfg.StrOpt('DOCTOR_PASSWD',
               default='doctor',
               help='openstack password for OpenStack service access',
               required=True),
    cfg.StrOpt('DOCTOR_PROJECT',
               default='doctor',
               help='openstack project for OpenStack service access',
               required=True),
    cfg.StrOpt('DOCTOR_ROLE',
               default='admin',
               help='the role of openstack user for OpenStack service access',
               required=True),
    cfg.StrOpt('ceilometer_version', default='2', help='ceilometer version'),
    cfg.StrOpt('glance_version', default='2', help='glance version'),
    cfg.FloatOpt('nova_version', default='2.11', help='Nova version'),
]


def prepare_service(args=None, conf=None, config_files=None):
    if conf is None:
        conf = cfg.ConfigOpts()

    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == 'DEFAULT' else group)

    conf(args, project='doctor', validate_default_values=True,
         default_config_files=config_files)

    return conf
