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
import re
import six
import stat
import subprocess
import time

from doctor_tests.common import utils
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import nova_client


@six.add_metaclass(abc.ABCMeta)
class BaseInstaller(object):
    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self.servers = list()
        self.use_containers = False

    @abc.abstractproperty
    def node_user_name(self):
        """user name for login to cloud node"""

    @abc.abstractmethod
    def get_ssh_key_from_installer(self):
        pass

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

    def setup_stunnel(self):
        self.log.info('Setup ssh stunnel in %s installer......'
                      % self.conf.installer.type)
        tunnels = [self.conf.consumer.port]
        if self.conf.test_case == 'maintenance':
            tunnel_uptime = 1200
            tunnels += [self.conf.app_manager.port, self.conf.inspector.port]
        elif self.conf.test_case == 'all':
            tunnel_uptime = 1800
            tunnels += [self.conf.app_manager.port, self.conf.inspector.port]
        else:
            tunnel_uptime = 600

        for node_ip in self.controllers:
            for port in tunnels:
                self.log.info('tunnel for port %s' % port)
                cmd = ("ssh -o UserKnownHostsFile=/dev/null"
                       " -o StrictHostKeyChecking=no"
                       " -i %s %s@%s -R %s:localhost:%s"
                       " sleep %s > ssh_tunnel.%s.%s"
                       " 2>&1 < /dev/null "
                       % (self.key_file,
                          self.node_user_name,
                          node_ip,
                          port,
                          port,
                          tunnel_uptime,
                          node_ip,
                          port))
                server = subprocess.Popen('exec ' + cmd, shell=True)
                self.servers.append(server)
        if self.conf.admin_tool.type == 'fenix':
            port = self.conf.admin_tool.port
            self.log.info('tunnel for port %s' % port)
            cmd = ("ssh -o UserKnownHostsFile=/dev/null"
                   " -o StrictHostKeyChecking=no"
                   " -i %s %s@%s -L %s:localhost:%s"
                   " sleep %s > ssh_tunnel.%s.%s"
                   " 2>&1 < /dev/null "
                   % (self.key_file,
                      self.node_user_name,
                      node_ip,
                      port,
                      port,
                      tunnel_uptime,
                      node_ip,
                      port))
            server = subprocess.Popen('exec ' + cmd, shell=True)
            self.servers.append(server)

    def _get_ssh_key(self, client, key_path):
        self.log.info('Get SSH keys from %s installer......'
                      % self.conf.installer.type)

        if self.key_file is not None:
            self.log.info('Already have SSH keys from %s installer......'
                          % self.conf.installer.type)
            return self.key_file

        ssh_key = '{0}/{1}'.format(utils.get_doctor_test_root_dir(),
                                   'instack_key')
        client.scp(key_path, ssh_key, method='get')
        user = getpass.getuser()
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(user).gr_gid
        os.chown(ssh_key, uid, gid)
        os.chmod(ssh_key, stat.S_IREAD)
        return ssh_key

    @abc.abstractmethod
    def get_transport_url(self):
        pass

    def _run_cmd_remote(self, client, command):
        self.log.info('Run command=%s in %s installer......'
                      % (command, self.conf.installer.type))

        ret, output = client.ssh(command)
        if ret:
            raise Exception('Exec command in %s installer failed,'
                            'ret=%s, output=%s'
                            % (self.conf.installer.type,
                               ret, output))
        self.log.info('Output=%s command=%s in %s installer'
                      % (output, command, self.conf.installer.type))
        return output

    def _check_cmd_remote(self, client, command):
        self.log.info('Check command=%s return in %s installer......'
                      % (command, self.conf.installer.type))

        ret, output = client.ssh(command, raise_enabled=False)
        self.log.info('return %s' % ret)
        if ret == 0:
            ret = True
        else:
            ret = False
        return ret

    @utils.run_async
    def _run_apply_patches(self, client, restart_cmd, script_names,
                           python='python3'):
        installer_dir = os.path.dirname(os.path.realpath(__file__))
        if isinstance(script_names, list):
            for script_name in script_names:
                script_abs_path = '{0}/{1}/{2}'.format(installer_dir,
                                                       'common', script_name)
                if self.conf.installer.type == "devstack":
                    script_name = "/opt/stack/%s" % script_name
                try:
                    client.scp(script_abs_path, script_name)
                except Exception:
                    client.scp(script_abs_path, script_name)
                try:
                    if ".py" in script_name:
                        cmd = 'sudo %s %s' % (python, script_name)
                    else:
                        cmd = 'sudo chmod 700 %s;sudo ./%s' % (script_name,
                                                               script_name)
                    ret, output = client.ssh(cmd)
                    self.log.info('Command %s output %s' % (cmd, output))
                except Exception:
                    ret, output = client.ssh(cmd)
                    self.log.info('Command %s output %s' % (cmd, output))
                if ret:
                    raise Exception('Do the command in remote'
                                    ' node failed, ret=%s, cmd=%s, output=%s'
                                    % (ret, cmd, output))
            if 'nova' in restart_cmd or 'devstack@n-' in restart_cmd:
                # Make sure scheduler has proper cpu_allocation_ratio
                time.sleep(5)
            client.ssh(restart_cmd)
