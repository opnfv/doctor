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

from doctor_tests.common.utils import get_doctor_test_root_dir
from doctor_tests.common.utils import SSHClient
from doctor_tests.identity_auth import get_session
from doctor_tests.installer.base import BaseInstaller
from doctor_tests.os_clients import nova_client


class DaisyInstaller(BaseInstaller):
    node_user_name = 'root'

    def __init__(self, conf, log):
        super(DaisyInstaller, self).__init__(conf, log)
        self.client = SSHClient(self.conf.installer.ip,
                                self.conf.installer.username,
                                password='r00tme')
        self.key_file = None
        self.controllers = list()
        self.servers = list()
        self.test_dir = get_doctor_test_root_dir()

    def setup(self):
        self.log.info('Setup Daisy installer start......')

        self.get_ssh_key_from_installer()
        self.get_controller_ips()
        self.create_flavor()
        self.setup_stunnel()

    def cleanup(self):
        for server in self.servers:
            server.terminate()

    def get_ssh_key_from_installer(self):
        self.log.info('Get SSH keys from Daisy installer......')

        if self.key_file is not None:
            self.log.info('Already have SSH keys from Daisy installer......')
            return self.key_file

        ssh_key = '{0}/{1}'.format(self.test_dir, 'instack_key')
        self.client.scp('/root/.ssh/id_dsa', ssh_key, method='get')
        user = getpass.getuser()
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(user).gr_gid
        os.chown(ssh_key, uid, gid)
        os.chmod(ssh_key, stat.S_IREAD)
        self.key_file = ssh_key
        return self.key_file

    def get_controller_ips(self):
        self.log.info('Get controller ips from Daisy installer......')

        command = "source daisyrc_admin; " \
                  "daisy host-list | grep 'CONTROLLER_LB' | cut -d '|' -f 3 "
        ret, controllers = self.client.ssh(command)
        if ret:
            raise Exception('Exec command to get controller ips'
                            'in Daisy installer failed'
                            'ret=%s, output=%s' % (ret, controllers))
        controller_ips = []
        for controller in controllers:
            controller_ips.append(self.get_host_ip_from_hostname(controller))
        self.log.info('Get controller_ips:%s from Daisy installer'
                      % controller_ips)
        self.controllers = controller_ips

    def get_host_ip_from_hostname(self, hostname):
        self.log.info('Get host ip from host name......')

        hostip = hostname.split('-')[1:]
        host_ip = '.'.join(hostip)
        self.log.info('Get host_ip:%s from host_name:%s'
                      % (host_ip, hostname))
        return host_ip

    def create_flavor(self):
        self.nova = \
            nova_client(self.conf.nova_version,
                        get_session())
        flavors = {flavor.name: flavor for flavor in self.nova.flavors.list()}
        if self.conf.flavor not in flavors:
            self.nova.flavors.create(self.conf.flavor, 512, 1, 1)

    def setup_stunnel(self):
        self.log.info('Setup ssh stunnel in controller nodes in Daisy installer......')
        for node_ip in self.controllers:
            cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s@%s -R %s:localhost:%s sleep 600 > ssh_tunnel.%s 2>&1 < /dev/null &" \
                  % (self.key_file, self.node_user_name, node_ip,
                     self.conf.consumer.port, self.conf.consumer.port, node_ip)
            server = subprocess.Popen(cmd, shell=True)
            self.servers.append(server)
            server.communicate()
