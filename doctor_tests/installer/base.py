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
class BaseInstaller(object):
    def __init__(self, conf, log):
        self.conf = conf
        self.log = log

    @abc.abstractproperty
    def node_user_name(self):
        """user name for login to cloud node"""

    @abc.abstractmethod
    def get_ssh_key_from_installer(self):
        pass

    @abc.abstractmethod
    def get_host_ip_from_hostname(self, hostname):
        pass

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def cleanup(self):
        pass
