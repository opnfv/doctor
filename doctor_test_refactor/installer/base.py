##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from oslo_utils import importutils

SUPPORTED_INSTALLER_TYPES = ['apex', 'fuel', 'local']

_installer_name_class_mapping = {
    'apex': 'doctor.doctor_test_refactor.installer.apex.ApexInstaller',
    'fuel': 'doctor.doctor_test_refactor.installer.fuel.FuelInstaller',
    'local': 'doctor.doctor_test_refactor.installer.local.LocalInstaller'
}

def get_installer(conf):
    if conf.installer_type not in SUPPORTED_INSTALLER_TYPES:
        raise Exception("Installer type '%s' not supported", conf.installer_type)

    installer_class = _installer_name_class_mapping[conf.installer_type]

    return importutils.import_object(installer_class, conf)



class Installer(object):

    def __init__(self, conf):
        self.conf = conf
        self.installer_ip = self.get_installer_ip()        

    def get_installer_ip(self):
        pass

    def is_installer_ip_exist(self):
        return True if self.installer_ip is not None else False
        
    def prepare_ssh_to_cloud(self):
        pass

    def get_compute_host_info(self):
        pass
    
    def prepare_test_env(self):
        pass
