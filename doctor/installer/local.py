##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import socket

from oslo_config import cfg

from doctor.installer.base import Installer


class LocalInstaller(Installer):

    def __init__(self, conf):
        super(LocalInstaller, self).__init__(conf)

    def get_installer_ip(self):
        return None

    def get_compute_ip_from_hostname(hostname):
        return socket.gethostbyname(hostname)

    def is_installer_ip_exist(self):
        return True 

    def prepare_ssh_to_cloud(self):
        pass

    def get_compute_host_info(self):
        pass
    
    def prepare_test_env(self):
        pass


