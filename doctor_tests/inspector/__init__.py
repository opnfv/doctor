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

from doctor_tests.common.constants import Inspector


OPTS = [
    cfg.StrOpt('type',
               default=os.environ.get('INSPECTOR_TYPE', Inspector.SAMPLE),
               choices=['sample', 'congress', 'vitrage'],
               help='the component of doctor inspector',
               required=True),
    cfg.StrOpt('ip',
               default='127.0.0.1',
               help='the host ip of inspector',
               required=False),
    cfg.StrOpt('port',
               default='12345',
               help='the port of default for inspector',
               required=False),
    cfg.BoolOpt('update_neutron_port_dp_status',
                default=False,
                help='Update data plane status of affected neutron ports',
                required=False),
]


_inspector_name_class_mapping = {
    Inspector.SAMPLE: 'doctor_tests.inspector.sample.SampleInspector',
    Inspector.CONGRESS: 'doctor_tests.inspector.congress.CongressInspector',
    Inspector.VITRAGE: 'doctor_tests.inspector.vitrage.VitrageInspector',
}


def get_inspector(conf, log, transport_url=None):
    inspector_class = _inspector_name_class_mapping[conf.inspector.type]
    if conf.inspector.type == 'sample':
        return importutils.import_object(inspector_class, conf, log,
                                         transport_url)
    else:
        return importutils.import_object(inspector_class, conf, log)
