##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os

from oslo_config import cfg
from oslo_utils import importutils

OPTS = [
    cfg.StrOpt('type',
               default=os.environ.get('INSTALLER_TYPE', 'local'),
               choices=['local', 'apex'],
               help='the type of installer',
               required=True),
    cfg.StrOpt('ip',
               default=os.environ.get('INSTALLER_IP', '127.0.0.1'),
               help='the ip of installer'),
    cfg.StrOpt('username',
               default='root',
               help='the user name for login installer server',
               required=True),
]


_installer_name_class_mapping = {
    'local': 'doctor_tests.installer.local.LocalInstaller',
    'apex': 'doctor_tests.installer.apex.ApexInstaller'
}


def get_installer(conf, log):
    installer_class = _installer_name_class_mapping[conf.installer.type]
    return importutils.import_object(installer_class, conf, log)
