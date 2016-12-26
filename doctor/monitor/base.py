##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from oslo_utils import importutils


_monitor_name_class_mapping = {
    'sample': 'doctor.monitor.sample.SampleMonitor'
}

def get_monitor(conf, inspector):
    monitor_class = _monitor_name_class_mapping.get(conf.monitor.type)
    return importutils.import_object(monitor_class, conf, inspector)


class Monitor(object):

    def __init__(self, conf):
        self.conf = conf

    def start(self):
        pass

    def stop(self):
        pass

