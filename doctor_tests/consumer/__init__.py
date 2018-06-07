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
               choices=['sample'],
               help='the component of doctor consumer',
               required=True),
    cfg.StrOpt('ip',
               default='127.0.0.1',
               help='the ip of consumer',
               required=True),
    cfg.IntOpt('port',
               default=12346,
               help='the port of doctor consumer',
               required=True),
]


_consumer_name_class_mapping = {
    'sample': 'doctor_tests.consumer.sample.SampleConsumer'
}


def get_consumer(conf, log):
    consumer_class = _consumer_name_class_mapping.get(conf.consumer.type)
    return importutils.import_object(consumer_class, conf, log)
