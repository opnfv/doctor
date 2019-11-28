##############################################################################
# Copyright (c) 2019 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import socket
import time

from doctor_tests.common.utils import SSHClient
from doctor_tests.common.utils import LocalSSH
from doctor_tests.identity_auth import get_session
from doctor_tests.installer.base import BaseInstaller
from doctor_tests.os_clients import nova_client


class DevstackInstaller(BaseInstaller):
    node_user_name = None
    cm_set_script = 'set_config.py'
    nc_set_compute_script = 'set_compute_config.py'
    cm_restore_script = 'restore_config.py'
    nc_restore_compute_script = 'restore_compute_config.py'
    ac_restart_script = 'restart_aodh.py'
    ac_restore_script = 'restore_aodh.py'
    python = 'python'

    def __init__(self, conf, log):
        super(DevstackInstaller, self).__init__(conf, log)
        # Run Doctor under users home. sudo hides other env param to be used
        home, self.node_user_name = (iter(os.environ.get('VIRTUAL_ENV')
                                     .split('/', 3)[1:3]))
        # Migration needs to work so ssh should have proper key defined
        self.key_file = '/%s/%s/.ssh/id_rsa' % (home, self.node_user_name)
        self.log.info('ssh uses: %s and %s' % (self.node_user_name,
                                               self.key_file))
        self.controllers = ([ip for ip in
                            socket.gethostbyname_ex(socket.gethostname())[2]
                            if not ip.startswith('127.')] or
                            [[(s.connect(('8.8.8.8', 53)),
                             s.getsockname()[0], s.close())
                             for s in [socket.socket(socket.AF_INET,
                                       socket.SOCK_DGRAM)]][0][1]])
        conf.admin_tool.ip = self.controllers[0]
        self.computes = list()
        self.nova = nova_client(conf.nova_version, get_session())

    def setup(self):
        self.log.info('Setup Devstack installer start......')
        self._get_devstack_conf()
        self.create_flavor()
        self.set_apply_patches()

    def cleanup(self):
        self.restore_apply_patches()

    def get_ssh_key_from_installer(self):
        return self.key_file

    def get_transport_url(self):
        client = LocalSSH(self.log)
        cmd = 'sudo grep -m1 "^transport_url" /etc/nova/nova.conf'
        ret, url = client.ssh(cmd)
        url = url.split("= ", 1)[1][:-1]
        self.log.info('get_transport_url %s' % url)
        return url

    def get_host_ip_from_hostname(self, hostname):
        return [hvisor.__getattr__('host_ip') for hvisor in self.hvisors
                if hvisor.__getattr__('hypervisor_hostname') == hostname][0]

    def _get_devstack_conf(self):
        self.log.info('Get devstack config details for Devstack installer'
                      '......')
        self.hvisors = self.nova.hypervisors.list(detailed=True)
        self.log.info('checking hypervisors.......')
        self.computes = [hvisor.__getattr__('host_ip') for hvisor in
                         self.hvisors]
        self.use_containers = False
        self.log.info('controller_ips:%s' % self.controllers)
        self.log.info('compute_ips:%s' % self.computes)
        self.log.info('use_containers:%s' % self.use_containers)

    def _set_docker_restart_cmd(self, service):
        # There can be multiple instances running so need to restart all
        cmd = "for container in `sudo docker ps | grep "
        cmd += service
        cmd += " | awk '{print $1}'`; do sudo docker restart $container; \
               done;"
        return cmd

    def set_apply_patches(self):
        self.log.info('Set apply patches start......')

        set_scripts = [self.cm_set_script]

        restart_cmd = 'sudo systemctl restart' \
                      ' devstack@ceilometer-anotification.service'

        client = LocalSSH(self.log)
        self._run_apply_patches(client,
                                restart_cmd,
                                set_scripts,
                                python=self.python)
        time.sleep(7)

        self.log.info('Set apply patches start......')

        if self.conf.test_case != 'fault_management':
            restart_cmd = 'sudo systemctl restart' \
                          ' devstack@n-cpu.service'
            for node_ip in self.computes:
                client = SSHClient(node_ip, self.node_user_name,
                                   key_filename=self.key_file)
                self._run_apply_patches(client,
                                        restart_cmd,
                                        [self.nc_set_compute_script],
                                        python=self.python)
            time.sleep(7)

    def restore_apply_patches(self):
        self.log.info('restore apply patches start......')

        restore_scripts = [self.cm_restore_script]

        restart_cmd = 'sudo systemctl restart' \
                      ' devstack@ceilometer-anotification.service'

        if self.conf.test_case != 'fault_management':
            restart_cmd += ' devstack@n-sch.service'
            restore_scripts.append(self.nc_restore_compute_script)

        client = LocalSSH(self.log)
        self._run_apply_patches(client,
                                restart_cmd,
                                restore_scripts,
                                python=self.python)

        if self.conf.test_case != 'fault_management':

            restart_cmd = 'sudo systemctl restart' \
                          ' devstack@n-cpu.service'
            for node_ip in self.computes:
                client = SSHClient(node_ip, self.node_user_name,
                                   key_filename=self.key_file)
                self._run_apply_patches(
                    client, restart_cmd,
                    [self.nc_restore_compute_script],
                    python=self.python)
