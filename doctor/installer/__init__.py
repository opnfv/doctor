##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os

from oslo_config import cfg


OPTS = [
    cfg.StrOpt('type',
               default=os.environ.get('INSTALLER_TYPE', 'local'),
               choices=('apex', 'fuel', 'local'),               
               help='the type of installer',
               required=True),
    cfg.ListOpt('path',
                default=['doctor.doctor.installer'],
                help='base path for installer'),
    cfg.StrOpt('installer_ip',
               default=os.environ.get('INSTALLER_IP', '127.0.0.1'),
               help='the ip of installer'),
    cfg.StrOpt('user',
               default='root',
               help='the user of the apex installer',
               required=True),
]