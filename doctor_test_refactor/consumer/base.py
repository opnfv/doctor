##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from oslo_utils import importutils

_consumer_name_class_mapping = {
    'sample': 'doctor.doctor_test_refactor.consumer.sample.SampleConsumer'
}


def get_consumer(conf):
    consumer_class = _consumer_name_class_mapping.get(conf.consumer_type)
    return importutils.import_object(consumer_class, conf)


class Consumer(object):

    def __init__(self, conf):
        self.conf = conf

    def start(self):
        pass


