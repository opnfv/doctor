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


class ApexInstaller(BaseInstaller):
    node_user_name = 'heat-admin'
    cm_set_script = 'set_ceilometer.py'
    cm_restore_script = 'restore_ceilometer.py'

    def __init__(self, conf, log):
        super(ApexInstaller, self).__init__(conf, log)
        self.client = SSHClient(self.conf.installer.ip,
                                self.conf.installer.username,
                                look_for_keys=True)
        self.controller_clients = list()

    def setup(self):
        self.log.info('Setup Apex installer start......')

        key_path = '/home/stack/.ssh/id_rsa'
        self.get_ssh_key_from_installer(key_path)

        command = "source stackrc; " \
                  "nova list | grep ' overcloud-controller-[0-9] ' " \
                  "| sed -e 's/^.*ctlplane=//' |awk '{print $1}'"
        self.controllers = self.get_controller_ips(self.client, command)

        self.create_flavor()
        self.set_apply_patches()
        self.setup_stunnel()

    def cleanup(self):
        self.restore_apply_patches()
        for server in self.servers:
            server.terminate()

    def get_host_ip_from_hostname(self, hostname):
        hostname_in_undercloud = hostname.split('.')[0]
        command = "source stackrc; nova show %s | awk '/ ctlplane network /{print $5}'" % (hostname_in_undercloud)   # noqa
        self._get_host_ip(self.client, command, hostname_in_undercloud)

    def set_apply_patches(self):
        self.log.info('Set apply patches start......')

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name,
                               key_filename=self.key_file)
            self.controller_clients.append(client)
            self._ceilometer_apply_patches(client, self.cm_set_script)
            client.ssh('sudo systemctl restart '
                       'openstack-ceilometer-notification.service')

    def restore_apply_patches(self):
        self.log.info('restore apply patches start......')

        for client in self.controller_clients:
            self._ceilometer_apply_patches(client, self.cm_restore_script)
            client.ssh('sudo systemctl restart '
                       'openstack-ceilometer-notification.service')
