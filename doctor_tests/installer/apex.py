##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import getpass
import grp
import os
import pwd
import stat
import subprocess
import sys

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
        self.key_file = None
        self.controllers = list()
        self.controller_clients = list()
        self.servers = list()

    def setup(self):
        self.log.info('Setup Apex installer start......')

        self.get_ssh_key_from_installer()
        self.get_controller_ips()
        self.set_apply_patches()
        self.setup_stunnel()

    def cleanup(self):
        self.restore_apply_patches()
        for server in self.servers:
            server.terminate()

    def get_ssh_key_from_installer(self):
        self.log.info('Get SSH keys from Apex installer......')

        if self.key_file is not None:
            self.log.info('Already have SSH keys from Apex installer......')
            return self.key_file

        self.client.scp('/home/stack/.ssh/id_rsa', './instack_key', method='get')
        user = getpass.getuser()
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(user).gr_gid
        os.chown('./instack_key', uid, gid)
        os.chmod('./instack_key', stat.S_IREAD)
        current_dir = os.curdir
        self.key_file = '{0}/{1}'.format(current_dir, 'instack_key')
        return self.key_file

    def get_controller_ips(self):
        self.log.info('Get controller ips from Apex installer......')

        command = "source stackrc; " \
                  "nova list | grep ' overcloud-controller-[0-9] ' " \
                  "| sed -e 's/^.*ctlplane=//' |awk '{print $1}'"
        ret, controllers = self.client.ssh(command)
        if ret:
            raise Exception('Exec command to get controller ips in Apex installer failed'
                            'ret=%s, output=%s' % (ret, controllers))
        self.log.info('Get controller_ips:%s from Apex installer' % controllers)
        self.controllers = controllers

    def get_host_ip_from_hostname(self, hostname):
        self.log.info('Get host ip from host name in Apex installer......')

        hostname_in_undercloud = hostname.split('.')[0]

        command = "source stackrc; nova show %s  | awk '/ ctlplane network /{print $5}'" % (hostname_in_undercloud)
        ret, host_ip = self.client.ssh(command)
        if ret:
            raise Exception('Exec command to get host ip from hostname(%s) in Apex installer failed'
                            'ret=%s, output=%s' % (hostname, ret, host_ip))
        self.log.info('Get host_ip:%s from host_name:%s in Apex installer' % (host_ip, hostname))
        return host_ip[0]

    def setup_stunnel(self):
        self.log.info('Setup ssh stunnel in controller nodes in Apex installer......')
        for node_ip in self.controllers:
            cmd = "sudo ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s@%s -R %s:localhost:%s sleep 600 > ssh_tunnel.%s.log 2>&1 < /dev/null &" \
                  % (self.key_file, self.node_user_name, node_ip,
                     self.conf.consumer.port, self.conf.consumer.port, node_ip)
            server = subprocess.Popen(cmd, shell=True)
            self.servers.append(server)
            server.communicate()

    def set_apply_patches(self):
        self.log.info('Set apply patches start......')

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name, key_filename=self.key_file)
            self.controller_clients.append(client)
            self._ceilometer_apply_patches(client, self.cm_set_script)

    def restore_apply_patches(self):
        self.log.info('restore apply patches start......')

        for client in self.controller_clients:
            self._ceilometer_apply_patches(client, self.cm_restore_script)

    def _ceilometer_apply_patches(self, ssh_client, script_name):
        installer_dir = os.path.dirname(os.path.realpath(__file__))
        script_abs_path = '{0}/{1}/{2}'.format(installer_dir, 'common', script_name)

        ssh_client.scp(script_abs_path, script_name)
        cmd = 'sudo python %s' % script_name
        ret, output = ssh_client.ssh(cmd)
        if ret:
            raise Exception('Do the ceilometer command in controller node failed....'
                            'ret=%s, cmd=%s, output=%s' % (ret, cmd, output))
        ssh_client.ssh('sudo systemctl restart openstack-ceilometer-notification.service')

