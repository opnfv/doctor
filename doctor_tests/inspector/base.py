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
class BaseInspector(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self._host_down_time = None
        self._vm_down_time = None

    @property
    def host_down_time(self):
        return self._host_down_time

    @host_down_time.setter
    def host_down_time(self, host_down_time):
        self._host_down_time = host_down_time

    @property
    def vm_down_time(self):
        return self._vm_down_time

    @vm_down_time.setter
    def vm_down_time(self, vm_down_time):
        self._vm_down_time = vm_down_time

    @abc.abstractmethod
    def get_inspector_url(self):
        pass

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass
