##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from oslo_utils import importutils


SUPPORTED_INSPECTOR_TYPES = ['sample', 'congress']

_inspector_name_class_mapping = {
    'sample': 'doctor.inspector.sample.SampleInspector',
    'congress': 'doctor.inspector.congress.CongressInspector'
}

def get_inspector(conf):
    if conf.inspector.type not in SUPPORTED_INSPECTOR_TYPES:
        raise Exception("Inspector type '%s' not supported", conf.inspector.type)

    inspector_class = _inspector_name_class_mapping[conf.inspector.type]

    return importutils.import_object(inspector_class, conf)


class Inspector(object):

    def __init__(self, conf):
        self.conf = conf
