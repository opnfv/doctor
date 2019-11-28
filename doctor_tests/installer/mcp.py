##############################################################################
# Copyright (c) 2019 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from os.path import isfile
import time

from doctor_tests.common.constants import is_fenix
from doctor_tests.common.utils import get_doctor_test_root_dir
from doctor_tests.common.utils import SSHClient
from doctor_tests.installer.base import BaseInstaller


class McpInstaller(BaseInstaller):
    node_user_name = 'ubuntu'

    cm_set_script = 'set_config.py'
    nc_set_compute_script = 'set_compute_config.py'
    fe_set_script = 'set_fenix.sh'
    cm_restore_script = 'restore_config.py'
    nc_restore_compute_script = 'restore_compute_config.py'
    ac_restart_script = 'restart_aodh.py'
    ac_restore_script = 'restore_aodh.py'
    python = 'python3'

    def __init__(self, conf, log):
        super(McpInstaller, self).__init__(conf, log)
        self.key_file = self.get_ssh_key_from_installer()
        self.client = SSHClient(self.conf.installer.ip,
                                self.node_user_name,
                                key_filename=self.key_file,
                                look_for_keys=True)
        self.controllers = list()
        self.controller_clients = list()
        self.computes = list()

    def setup(self):
        self.log.info('Setup MCP installer start......')
        self.get_node_ips()
        self.create_flavor()
        if is_fenix(self.conf):
            self.set_apply_patches()
        self.setup_stunnel()

    def cleanup(self):
        if is_fenix(self.conf):
            self.restore_apply_patches()
        for server in self.servers:
            server.terminate()

    def get_ssh_key_from_installer(self):
        self.log.info('Get SSH keys from MCP......')

        # Default in path /var/lib/opnfv/mcp.rsa
        ssh_key = '/root/.ssh/id_rsa'
        mcp_key = '/var/lib/opnfv/mcp.rsa'
        return mcp_key if isfile(mcp_key) else ssh_key

    def get_transport_url(self):
        client = SSHClient(self.controllers[0], self.node_user_name,
                           key_filename=self.key_file)
        try:
            cmd = 'sudo grep -m1 "^transport_url" /etc/nova/nova.conf'
            ret, url = client.ssh(cmd)

            if ret:
                raise Exception('Exec command to get transport from '
                                'controller(%s) in MCP installer failed, '
                                'ret=%s, output=%s'
                                % (self.controllers[0], ret, url))
            elif self.controllers[0] not in url:
                # need to use ip instead of hostname
                url = (re.sub("@.*:", "@%s:" % self.controllers[0],
                       url[0].split("=", 1)[1]))
        except Exception:
            cmd = 'grep -i "^rabbit" /etc/nova/nova.conf'
            ret, lines = client.ssh(cmd)
            if ret:
                raise Exception('Exec command to get transport from '
                                'controller(%s) in MCP installer failed, '
                                'ret=%s, output=%s'
                                % (self.controllers[0], ret, url))
            else:
                for line in lines.split('\n'):
                    if line.startswith("rabbit_userid"):
                        rabbit_userid = line.split("=")
                    if line.startswith("rabbit_port"):
                        rabbit_port = line.split("=")
                    if line.startswith("rabbit_password"):
                        rabbit_password = line.split("=")
                url = "rabbit://%s:%s@%s:%s/?ssl=0" % (rabbit_userid,
                                                       rabbit_password,
                                                       self.controllers[0],
                                                       rabbit_port)
        self.log.info('get_transport_url %s' % url)
        return url

    def _copy_overcloudrc_to_controllers(self):
        for ip in self.controllers:
            cmd = "scp overcloudrc %s@%s:" % (self.node_user_name, ip)
            self._run_cmd_remote(self.client, cmd)

    def get_node_ips(self):
        self.log.info('Get node ips from Mcp installer......')

        command = 'sudo salt "*" --out yaml pillar.get _param:single_address'
        node_details = self._run_cmd_remote(self.client, command)

        self.controllers = [line.split()[1] for line in node_details
                            if line.startswith("ctl")]
        self.computes = [line.split()[1] for line in node_details
                         if line.startswith("cmp")]

        self.log.info('controller_ips:%s' % self.controllers)
        self.log.info('compute_ips:%s' % self.computes)

    def get_host_ip_from_hostname(self, hostname):
        command = "sudo salt --out yaml '%s*' " \
                  "pillar.get _param:single_address |" \
                  "awk '{print $2}'" % hostname
        host_ips = self._run_cmd_remote(self.client, command)
        return host_ips[0]

    def set_apply_patches(self):
        self.log.info('Set apply patches start......')
        fenix_files = None

        set_scripts = [self.cm_set_script]

        restart_cmd = 'sudo systemctl restart' \
                      ' ceilometer-agent-notification.service'

        if self.conf.test_case != 'fault_management':
            if is_fenix(self.conf):
                set_scripts.append(self.fe_set_script)
                testdir = get_doctor_test_root_dir()
                fenix_files = ["Dockerfile", "run"]
            restart_cmd += ' nova-scheduler.service'
            set_scripts.append(self.nc_set_compute_script)

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name,
                               key_filename=self.key_file)
            if fenix_files is not None:
                for fenix_file in fenix_files:
                    src_file = '{0}/{1}/{2}'.format(testdir,
                                                    'admin_tool/fenix',
                                                    fenix_file)
                    client.scp(src_file, fenix_file)
            self._run_apply_patches(client,
                                    restart_cmd,
                                    set_scripts,
                                    python=self.python)
        time.sleep(5)

        self.log.info('Set apply patches start......')

        if self.conf.test_case != 'fault_management':
            restart_cmd = 'sudo systemctl restart nova-compute.service'
            for node_ip in self.computes:
                client = SSHClient(node_ip, self.node_user_name,
                                   key_filename=self.key_file)
                self._run_apply_patches(client,
                                        restart_cmd,
                                        [self.nc_set_compute_script],
                                        python=self.python)
            time.sleep(5)

    def restore_apply_patches(self):
        self.log.info('restore apply patches start......')

        restore_scripts = [self.cm_restore_script]

        restore_scripts.append(self.ac_restore_script)
        restart_cmd = 'sudo systemctl restart' \
                      ' ceilometer-agent-notification.service'

        if self.conf.test_case != 'fault_management':
            restart_cmd += ' nova-scheduler.service'
            restore_scripts.append(self.nc_restore_compute_script)

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name,
                               key_filename=self.key_file)
            self._run_apply_patches(client,
                                    restart_cmd,
                                    restore_scripts,
                                    python=self.python)

        if self.conf.test_case != 'fault_management':
            restart_cmd = 'sudo systemctl restart nova-compute.service'
            for node_ip in self.computes:
                client = SSHClient(node_ip, self.node_user_name,
                                   key_filename=self.key_file)
                self._run_apply_patches(
                    client, restart_cmd,
                    [self.nc_restore_compute_script],
                    python=self.python)
