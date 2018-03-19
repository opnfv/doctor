##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import abc
import getpass
import grp
import os
import pwd
import six
import stat
import subprocess

from doctor_tests.common.utils import get_doctor_test_root_dir
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import nova_client


@six.add_metaclass(abc.ABCMeta)
class BaseInstaller(object):
    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self.key_file = None
        self.controllers = list()
        self.servers = list()

    @abc.abstractproperty
    def node_user_name(self):
        """user name for login to cloud node"""

    @abc.abstractmethod
    def get_ssh_key_from_installer(self, key_path):
        self.log.info('Get SSH keys from %s installer......'
                      % self.conf.installer.type)

        if self.key_file is not None:
            self.log.info('Already have SSH keys from %s installer......'
                          % self.conf.installer.type)
            return self.key_file

        ssh_key = '{0}/{1}'.format(get_doctor_test_root_dir(), 'instack_key')
        self.client.scp(key_path, ssh_key, method='get')
        user = getpass.getuser()
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(user).gr_gid
        os.chown(ssh_key, uid, gid)
        os.chmod(ssh_key, stat.S_IREAD)
        self.key_file = ssh_key
        return self.key_file

    @abc.abstractmethod
    def get_host_ip_from_hostname(self, hostname):
        pass

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def cleanup(self):
        pass

    def create_flavor(self):
        self.nova = \
            nova_client(self.conf.nova_version,
                        get_session())
        flavors = {flavor.name: flavor for flavor in self.nova.flavors.list()}
        if self.conf.flavor not in flavors:
            self.nova.flavors.create(self.conf.flavor, 512, 1, 1)

    def get_controller_ips(self, client, command):
        self.log.info('Get controller ips from %s installer......'
                      % self.conf.installer.type)

        ret, controllers = client.ssh(command)
        if ret:
            raise Exception('Exec command to get controller ips'
                            'in %s installer failed, ret=%s, output=%s'
                            % (self.conf.installer.type, ret, controllers))
        self.log.info('Get controller_ips:%s from %s installer'
                      % (controllers, self.conf.installer.type))
        return controllers

    def setup_stunnel(self):
        self.log.info('Setup ssh stunnel in %s installer......'
                      % self.conf.installer.type)

        for node_ip in self.controllers:
            cmd = ("ssh -o UserKnownHostsFile=/dev/null"
                   " -o StrictHostKeyChecking=no"
                   " -i %s %s@%s -R %s:localhost:%s"
                   " sleep 600 > ssh_tunnel.%s.log"
                   " 2>&1 < /dev/null &"
                   % (self.key_file,
                      self.node_user_name,
                      node_ip,
                      self.conf.consumer.port,
                      self.conf.consumer.port,
                      node_ip))
            server = subprocess.Popen(cmd, shell=True)
            self.servers.append(server)
            server.communicate()

    def _get_host_ip(self, client, command, hostname):
        self.log.info('Get host ip from host name=%s in %s installer......'
                      % (hostname, self.conf.installer.type))

        ret, host_ip = client.ssh(command)
        if ret:
            raise Exception('Exec command to get host ip from hostname(%s)'
                            'in %s installer failed, ret=%s, output=%s'
                            % (hostname, self.conf.installer.type,
                               ret, host_ip))
        self.log.info('Get host_ip:%s from host_name:%s in %s installer'
                      % (host_ip, hostname, self.conf.installer.type))
        return host_ip[0]

    def _ceilometer_apply_patches(self, ssh_client, script_name):
        installer_dir = os.path.dirname(os.path.realpath(__file__))
        script_abs_path = '{0}/{1}/{2}'.format(installer_dir,
                                               'common', script_name)

        ssh_client.scp(script_abs_path, script_name)
        cmd = 'sudo python %s' % script_name
        ret, output = ssh_client.ssh(cmd)
        if ret:
            raise Exception('Do the ceilometer command in controller'
                            ' node failed, ret=%s, cmd=%s, output=%s'
                            % (ret, cmd, output))
