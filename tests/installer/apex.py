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
import sys

from installer.base import BaseInstaller
from utils import SSHClient


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

    def setup(self):
        self.log.info('Setup Apex installer start......')

        self.key_file = self.get_ssh_key_from_installer()
        self.get_controller_ips()
        self.set_apply_patches()

    def cleanup(self):
        self.restore_apply_patches()

    def get_ssh_key_from_installer(self):
        self.log.info('Get SSH keys from Apex installer......')

        self.client.scp('/home/stack/.ssh/id_rsa', './instack_key', method='get')
        user = getpass.getuser()
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(user).gr_gid
        os.chown('./instack_key', uid, gid)
        os.chmod('./instack_key', stat.S_IREAD)
        current_dir = sys.path[0]
        return '{0}/{1}'.format(current_dir, 'instack_key')

    def get_controller_ips(self):
        self.log.info('Get controller ips from Apex installer......')

        command = "source stackrc; " \
                  "nova list | grep ' overcloud-controller-[0-9] ' " \
                  "| sed -e 's/^.*ctlplane=//' |awk '{print $1}'"
        ret, controllers = self.client.ssh(command)
        if ret:
            raise Exception('Exec command to get controller ips in Apex installer failed'
                            'ret=%s, output=%s' % (ret, controllers))
        self.controllers = controllers

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

