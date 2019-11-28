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
               default=os.environ.get('INSTALLER_TYPE', 'devstack'),
               choices=['local', 'apex', 'daisy', 'fuel', 'devstack'],
               help='the type of installer',
               required=True),
    cfg.StrOpt('ip',
               default=os.environ.get('INSTALLER_IP', '127.0.0.1'),
               help='the ip of installer'),
    cfg.StrOpt('key_file',
               default=os.environ.get('SSH_KEY', None),
               help='the key for user to login installer server',
               required=False),
]


_installer_name_class_mapping = {
    'local': 'doctor_tests.installer.local.LocalInstaller',
    'apex': 'doctor_tests.installer.apex.ApexInstaller',
    'daisy': 'doctor_tests.installer.daisy.DaisyInstaller',
    'fuel': 'doctor_tests.installer.mcp.McpInstaller',
    'devstack': 'doctor_tests.installer.devstack.DevstackInstaller'
}


def get_installer(conf, log):
    installer_class = _installer_name_class_mapping[conf.installer.type]
    return importutils.import_object(installer_class, conf, log)
