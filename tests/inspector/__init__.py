#############################################################################
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
               default=os.environ.get('INSPECTOR_TYPE', 'sample'),
               choices=['sample', 'congress', 'vitrage'],
               help='the component of doctor inspector',
               required=True),
    cfg.StrOpt('ip',
               default='127.0.0.1',
               help='the ip of default inspector',
               required=False),
    cfg.StrOpt('port',
               default='12345',
               help='the port of default for inspector',
               required=False),
]


_inspector_name_class_mapping = {
    'sample': 'inspector.sample.SampleInspector',
    'congress': 'inspector.congress.CongressInspector',
}

def get_inspector(conf, log):
    inspector_class = _inspector_name_class_mapping[conf.inspector.type]
    return importutils.import_object(inspector_class, conf, log)
