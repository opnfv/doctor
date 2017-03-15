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

import os_clients


IMAGE_OPTS = [
    cfg.StrOpt('name',
               default=os.environ.get('IMAGE_NAME', 'cirros'),
               help='the name of test image',
               required=True),
    cfg.StrOpt('format',
               default='qcow2',
               help='the format of test image',
               required=True),
    cfg.StrOpt('file_name',
               default='cirros.img',
               help='the name of image file',
               required=True),
    cfg.StrOpt('url',
               default='https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img',
               help='the url where to get the image',
               required=True),
]


DEFAULT_OPTS = [
    cfg.StrOpt('test_user',
               default='doctor',
               help='the name of test user',
               required=True),
    cfg.StrOpt('test_password',
               default='doctor',
               help='the password of test user',
               required=True),
    cfg.StrOpt('test_project',
               default='doctor',
               help='the name of test project',
               required=True),
    cfg.StrOpt('role',
               default='admin',
               help='the role of test user',
               required=True),
]


def list_opts():
    return [
        ('keystone_auth', os_clients.OPTS),
        ('image', IMAGE_OPTS),
        ('DEFAULT', DEFAULT_OPTS),
    ]

