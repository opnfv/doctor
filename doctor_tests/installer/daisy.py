##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from doctor_tests.common.utils import SSHClient
from doctor_tests.installer.base import BaseInstaller


class DaisyInstaller(BaseInstaller):
    node_user_name = 'root'

    def __init__(self, conf, log):
        super(DaisyInstaller, self).__init__(conf, log)
        self.client = SSHClient(self.conf.installer.ip,
                                self.conf.installer.username,
                                password='r00tme')
        self.key_file = None
        self.controllers = list()
        self.controller_clients = list()

    def setup(self):
        self.log.info('Setup Daisy installer start......')

        self.key_file = self.get_ssh_key_from_installer()
        self.controllers = self.get_controller_ips()
        self.create_flavor()
        self.setup_stunnel()

    def cleanup(self):
        for server in self.servers:
            server.terminate()

    def get_ssh_key_from_installer(self):
        key_path = '/root/.ssh/id_dsa'
        return self._get_ssh_key(self.client, key_path)

    def get_controller_ips(self):
        self.log.info('Get controller ips from Daisy installer......')

        command = "source daisyrc_admin; " \
                  "daisy host-list | grep 'CONTROLLER_LB' | cut -d '|' -f 3 "
        controller_names = self._run_cmd_remote(self.client, command)
        controllers = \
            [self.get_host_ip_from_hostname(controller)
             for controller in controller_names]
        self.log.info('Get controller_ips:%s from Daisy installer'
                      % controllers)
        return controllers

    def get_host_ip_from_hostname(self, hostname):
        self.log.info('Get host ip from host name......')

        hostip = hostname.split('-')[1:]
        host_ip = '.'.join(hostip)
        self.log.info('Get host_ip:%s from host_name:%s'
                      % (host_ip, hostname))
        return host_ip
