##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from oslo_config import cfg

from doctor.doctor_test_refactor.installer.base import Installer

LOCAL_INSTALLER = 'local'

OPTS = [
    cfg.StrOpt('installer_ip',
               default='127.0.0.1',
               help='the ip of installer'),
     cfg.StrOpt('installer_default_user',
               default='root',              
               help='the user of the apex installer',
               required=True),
]

class LocalInstaller(Installer):

    def __init__(self, conf):
        super(LocalInstaller, self).__init__(conf)

    def get_installer_ip(self):
        return None

    def is_installer_ip_exist(self):
        return True 

    def prepare_ssh_to_cloud(self):
        pass

    def get_compute_host_info(self):
        pass
    
    def prepare_test_env(self):
        pass


