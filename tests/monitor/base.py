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
class BaseMonitor(object):
    """Monitor computer fault and report error to the inspector"""
    def __init__(self, conf, installer, inspector_url, log):
        self.conf = conf
        self.log = log
        self.installer = installer
        self.inspector_url = inspector_url

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass
