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
    cfg.StrOpt('vm_name',
               default='doctor_vm',
               help='the name of test vm',
               required=True),
    cfg.IntOpt('vm_count',
               default=os.environ.get('VM_COUNT', 1),
               help='the name of test vm',
               required=True),
    cfg.StrOpt('vm_flavor',
               default='m1.tiny',
               help='the flavor of test vm',
               required=True),
    cfg.StrOpt('alarm_name',
               default='doctor_alarm1',
               help='the name of test alarm',
               required=True),
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
               default='_member_',
               help='the role of test user',
               required=True),
]