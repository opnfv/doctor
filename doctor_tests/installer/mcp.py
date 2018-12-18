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

    def __init__(self, conf, log):
        super(McpInstaller, self).__init__(conf, log)
        self.key_file = self.get_ssh_key_from_installer()
        self.client = SSHClient(self.conf.installer.ip,
                                self.node_user_name,
                                key_filename=self.key_file,
                                look_for_keys=True)
        self.controllers = list()
        self.controller_clients = list()

    def setup(self):
        self.log.info('Setup MCP installer start......')

        self.controllers = self.get_controller_ips()
        self.create_flavor()
        self.set_apply_patches()
        self.setup_stunnel()

    def cleanup(self):
        self.restore_apply_patches()
        for server in self.servers:
            server.terminate()

    def get_ssh_key_from_installer(self):
        self.log.info('Get SSH keys from MCP......')

        # Assuming mcp.rsa is already mapped to functest container
        # if not, only the test runs on jumphost can get the ssh_key
        # default in path /var/lib/opnfv/mcp.rsa
        ssh_key = '/root/.ssh/id_rsa'
        mcp_key = '/var/lib/opnfv/mcp.rsa'
        return ssh_key if isfile(ssh_key) else mcp_key

    def get_controller_ips(self):
        self.log.info('Get controller ips from Mcp installer......')

        command = "sudo salt --out yaml 'ctl*' " \
                  "pillar.get _param:openstack_control_address |" \
                  "awk '{print $2}'"
        controllers = self._run_cmd_remote(self.client, command)
        self.log.info('Get controller_ips:%s from Mcp installer'
                      % controllers)
        return controllers

    def get_host_ip_from_hostname(self, hostname):
        command = "sudo salt --out yaml '%s*' " \
                  "pillar.get _param:single_address |" \
                  "awk '{print $2}'" % hostname
        host_ips = self._run_cmd_remote(self.client, command)
        return host_ips[0]

    def set_apply_patches(self):
        self.log.info('Set apply patches start......')

    def restore_apply_patches(self):
        self.log.info('restore apply patches start......')
