##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseConsumer(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self._notified_time = None

    @property
    def notified_time(self):
        return self._notified_time

    @notified_time.setter
    def notified_time(self, notified_time):
        self._notified_time = notified_time

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass
