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
import re
import stat
import subprocess
import time

from doctor_tests.common.utils import get_doctor_test_root_dir
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
        self.servers = list()
        self.test_dir = get_doctor_test_root_dir()

    def setup(self):
        self.log.info('Setup Apex installer start......')
 
        self.get_ssh_key_from_installer()
        self.get_controller_ips()
        self.create_flavor()
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

        ssh_key = '{0}/{1}'.format(self.test_dir, 'instack_key')
        self.client.scp('/home/stack/.ssh/id_rsa', ssh_key, method='get')
        user = getpass.getuser()
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(user).gr_gid
        os.chown(ssh_key, uid, gid)
        os.chmod(ssh_key, stat.S_IREAD)
        self.key_file = ssh_key
        return self.key_file

    def get_controller_ips(self):
        self.log.info('Get controller ips from Apex installer......')

        command = "source stackrc; " \
                  "nova list | grep ' overcloud-controller-[0-9] ' " \
                  "| sed -e 's/^.*ctlplane=//' |awk '{print $1}'"
        ret, controllers = self.client.ssh(command)
        if ret:
            raise Exception('Exec command to get controller ips'
                            'in Apex installer failed, ret=%s, output=%s'
                            % (ret, controllers))
        self.log.info('Get controller_ips:%s from Apex installer'
                      % controllers)
        self.controllers = controllers

    def get_host_ip_from_hostname(self, hostname):
        self.log.info('Get host ip from host name in Apex installer......')

        hostname_in_undercloud = hostname.split('.')[0]

        command = "source stackrc; nova show %s | awk '/ ctlplane network /{print $5}'" % (hostname_in_undercloud)   # noqa
        ret, host_ip = self.client.ssh(command)
        if ret:
            raise Exception('Exec command to get host ip from hostname(%s)'
                            'in Apex installer failed, ret=%s, output=%s'
                            % (hostname, ret, host_ip))
        self.log.info('Get host_ip:%s from host_name:%s in Apex installer'
                      % (host_ip, hostname))
        return host_ip[0]

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

    def setup_stunnel(self):
        self.log.info('Setup ssh stunnel in controller nodes '
                      'in Apex installer......')

        tunnels = [self.conf.consumer.port]
        tunnel_uptime = 600

        for node_ip in self.controllers:
            for port in tunnels:
                self.log.info('tunnel for port %s' % port)
                cmd = ("ssh -o UserKnownHostsFile=/dev/null"
                       " -o StrictHostKeyChecking=no"
                       " -i %s %s@%s -R %s:localhost:%s"
                       " sleep %s > ssh_tunnel.%s.log"
                       " 2>&1 < /dev/null &"
                       % (self.key_file,
                          self.node_user_name,
                          node_ip,
                          port,
                          port,
                          tunnel_uptime,
                          node_ip))
                server = subprocess.Popen(cmd, shell=True)
                self.servers.append(server)
                server.communicate()

    def set_apply_patches(self):
        self.log.info('Set apply patches start......')

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name,
                               key_filename=self.key_file)
            self.controller_clients.append(client)
            self._config_apply_patches(client, self.cm_set_script)
        time.sleep(10)

    def restore_apply_patches(self):
        self.log.info('restore apply patches start......')

        for client in self.controller_clients:
            self._config_apply_patches(client, self.cm_restore_script)

    def _config_apply_patches(self, ssh_client, script_name):
        installer_dir = os.path.dirname(os.path.realpath(__file__))
        script_abs_path = '{0}/{1}/{2}'.format(installer_dir,
                                               'common', script_name)

        ssh_client.scp(script_abs_path, script_name)
        cmd = 'sudo python %s' % script_name
        ret, output = ssh_client.ssh(cmd)
        if ret:
            raise Exception('Do the config command in controller'
                            ' node failed, ret=%s, cmd=%s, output=%s'
                            % (ret, cmd, output))
        else:
            self.log.info('patches done, restart needed services......')
        cmd = ('sudo systemctl restart openstack-ceilometer-notification'
               '.service openstack-nova*')
        ret, output = ssh_client.ssh(cmd)
        if ret:
            raise Exception('Restart services failed ret=%s, cmd=%s, output=%s'
                            % (ret, cmd, output))
        else:
            self.log.info('services restarted......')
