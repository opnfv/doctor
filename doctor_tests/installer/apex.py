##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import re
import time

from doctor_tests.common.utils import SSHClient
from doctor_tests.installer.base import BaseInstaller


class ApexInstaller(BaseInstaller):
    node_user_name = 'heat-admin'
    cm_set_script = 'set_config.py'
    cm_restore_script = 'restore_config.py'

    def __init__(self, conf, log):
        super(ApexInstaller, self).__init__(conf, log)
        self.client = SSHClient(self.conf.installer.ip,
                                self.conf.installer.username,
                                look_for_keys=True)
        self.key_file = None
        self.controllers = list()
        self.controller_clients = list()

    def setup(self):
        self.log.info('Setup Apex installer start......')

        self.key_file = self.get_ssh_key_from_installer()
        self.controllers = self.get_controller_ips()
        self.create_flavor()
        self.set_apply_patches()
        self.setup_stunnel()

    def cleanup(self):
        self.restore_apply_patches()
        for server in self.servers:
            server.terminate()

    def get_ssh_key_from_installer(self):
        key_path = '/home/stack/.ssh/id_rsa'
        return self._get_ssh_key(self.client, key_path)

    def get_controller_ips(self):
        self.log.info('Get controller ips from Apex installer......')

        command = "source stackrc; " \
                  "nova list | grep ' overcloud-controller-[0-9] ' " \
                  "| sed -e 's/^.*ctlplane=//' |awk '{print $1}'"
        controllers = self._run_cmd_remote(self.client, command)
        self.log.info('Get controller_ips:%s from Apex installer'
                      % controllers)
        return controllers

    def get_host_ip_from_hostname(self, hostname):
        self.log.info('Get host ip by hostname=%s from Apex installer......'
                      % hostname)

        hostname_in_undercloud = hostname.split('.')[0]
        command = "source stackrc; nova show %s | awk '/ ctlplane network /{print $5}'" % (hostname_in_undercloud)   # noqa
        host_ips = self._run_cmd_remote(self.client, command)
        return host_ips[0]

    def get_transport_url(self):
        client = SSHClient(self.controllers[0], self.node_user_name,
                           key_filename=self.key_file)

        command = 'sudo grep "^transport_url" /etc/nova/nova.conf'
        ret, url = client.ssh(command)
        if ret:
            raise Exception('Exec command to get host ip from controller(%s)'
                            'in Apex installer failed, ret=%s, output=%s'
                            % (self.controllers[0], ret, url))
        # need to use ip instead of hostname
        ret = (re.sub("@.*:", "@%s:" % self.controllers[0],
               url[0].split("=", 1)[1]))
        self.log.debug('get_transport_url %s' % ret)
        return ret

    def set_apply_patches(self):
        self.log.info('Set apply patches start......')

        restart_cm_cmd = 'sudo systemctl restart ' \
                         'openstack-ceilometer-notification.service' \
                         ' openstack-nova*'

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name,
                               key_filename=self.key_file)
            self.controller_clients.append(client)
            self._run_apply_patches(client,
                                    restart_cm_cmd,
                                    self.cm_set_script)
        time.sleep(10)

    def restore_apply_patches(self):
        self.log.info('restore apply patches start......')

        restart_cm_cmd = 'sudo systemctl restart ' \
                         'openstack-ceilometer-notification.service' \
                         ' openstack-nova*'

        for client in self.controller_clients:
            self._run_apply_patches(client,
                                    restart_cm_cmd,
                                    self.cm_restore_script)
