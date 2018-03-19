##############################################################################
# Copyright (c) 2018 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from os.path import isfile

from doctor_tests.common.utils import SSHClient
from doctor_tests.installer.base import BaseInstaller


class McpInstaller(BaseInstaller):
    node_user_name = 'ubuntu'
    cm_set_script = 'set_ceilometer.py'
    cm_restore_script = 'restore_ceilometer.py'

    def __init__(self, conf, log):
        super(McpInstaller, self).__init__(conf, log)
        self.client = None
        self.controller_clients = list()

    def setup(self):
        self.log.info('Setup MCP installer start......')

        key_path = '/var/lib/opnfv/mcp.rsa'
        self.get_ssh_key_from_installer(key_path)

        self.client = SSHClient(self.conf.installer.ip,
                                self.node_user_name,
                                key_filename=self.key_file)

        command = "sudo salt --out yaml 'ctl*' " \
                  "pillar.get _param:openstack_control_address |" \
                  "awk '{print $2}'"
        self.controllers = self.get_controller_ips(self.client, command)

        self.create_flavor()
        self.set_apply_patches()
        self.setup_stunnel()

    def cleanup(self):
        self.restore_apply_patches()
        for server in self.servers:
            server.terminate()

    def get_ssh_key_from_installer(self, key_path):
        self.log.info('Get SSH keys from MCP......')

        # Assuming mcp.rsa is already mapped to functest container
        # if not, only the test runs on jumphost can get the ssh_key
        # default in path /var/lib/opnfv/mcp.rsa
        ssh_key = '/root/.ssh/id_rsa'
        self.key_file = ssh_key if isfile(ssh_key) else key_path
        return self.key_file

    def get_host_ip_from_hostname(self, hostname):
        command = "sudo salt --out yaml '%s*' " \
                  "pillar.get _param:single_address |" \
                  "awk '{print $2}'" % hostname
        self._get_host_ip(self.client, command, hostname)

    def set_apply_patches(self):
        self.log.info('Set apply patches start......')

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name,
                               key_filename=self.key_file)
            self.controller_clients.append(client)
            self._ceilometer_apply_patches(client, self.cm_set_script)
            client.ssh('sudo service ceilometer-agent-notification restart')

    def restore_apply_patches(self):
        self.log.info('restore apply patches start......')

        for client in self.controller_clients:
            self._ceilometer_apply_patches(client, self.cm_restore_script)
            client.ssh('sudo service ceilometer-agent-notification restart')
