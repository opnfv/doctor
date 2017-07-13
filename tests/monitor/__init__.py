##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from oslo_config import cfg
from oslo_utils import importutils

OPTS = [
    cfg.StrOpt('type',
               default='sample',
               choices=['sample', 'collectd'],
               help='the type of doctor monitor component',
               required=True),
]


_monitor_name_class_mapping = {
    'sample': 'monitor.sample.SampleMonitor',
    'collectd': 'monitor.collectd.CollectdMonitor'
}

def get_monitor(conf, inspector_url, log):
    monitor_class = _monitor_name_class_mapping.get(conf.monitor.type)
    return importutils.import_object(monitor_class, conf,
                                     inspector_url, log)
