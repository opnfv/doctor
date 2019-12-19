##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from oslo_config import cfg
from oslo_utils import importutils
import os


OPTS = [
    cfg.StrOpt('type',
               default=os.environ.get('APP_MANAGER_TYPE', 'sample'),
               choices=['sample', 'vnfm'],
               help='the component of doctor app manager',
               required=True),
    cfg.StrOpt('ip',
               default='127.0.0.1',
               help='the ip of app manager',
               required=True),
    cfg.IntOpt('port',
               default='12348',
               help='the port of doctor app manager',
               required=True),
]


_app_manager_name_class_mapping = {
    'sample': 'doctor_tests.app_manager.sample.SampleAppManager',
    'vnfm': 'doctor_tests.app_manager.vnfm.VNFM',
}


def get_app_manager(stack, conf, log):
    app_manager_class = (
        _app_manager_name_class_mapping.get(conf.app_manager.type))
    return importutils.import_object(app_manager_class, stack, conf, log)
