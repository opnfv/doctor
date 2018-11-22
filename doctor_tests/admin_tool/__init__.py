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
               default=os.environ.get('ADMIN_TOOL_TYPE', 'sample'),
               choices=['sample', 'fenix'],
               help='the component of doctor admin_tool',
               required=True),
    cfg.StrOpt('ip',
               default='0.0.0.0',
               help='the ip of admin_tool',
               required=True),
    cfg.IntOpt('port',
               default='12347',
               help='the port of doctor admin_tool',
               required=True),
]


_admin_tool_name_class_mapping = {
    'sample': 'doctor_tests.admin_tool.sample.SampleAdminTool'
}


def get_admin_tool(trasport_url, conf, log):
    admin_tool_class = _admin_tool_name_class_mapping.get(conf.admin_tool.type)
    return importutils.import_object(admin_tool_class, trasport_url, conf, log)
