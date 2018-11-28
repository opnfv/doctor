##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import time

from doctor_tests.common.constants import Inspector
from doctor_tests.common.utils import SSHClient
from doctor_tests.installer.base import BaseInstaller


class ApexInstaller(BaseInstaller):
    node_user_name = 'heat-admin'
    installer_username = 'stack'
    cm_set_script = 'set_config.py'
    nc_set_compute_script = 'set_compute_config.py'
    cg_set_script = 'set_congress.py'
    cm_restore_script = 'restore_config.py'
    nc_restore_compute_script = 'restore_compute_config.py'
    cg_restore_script = 'restore_congress.py'
    ac_restart_script = 'restart_aodh.py'
    ac_restore_script = 'restore_aodh.py'
    python = 'python'

    def __init__(self, conf, log):
        super(ApexInstaller, self).__init__(conf, log)
        self.client = SSHClient(self.conf.installer.ip,
                                self.installer_username,
                                key_filename=self.conf.installer.key_file,
                                look_for_keys=True)
        self.key_file = None
        self.controllers = list()
        self.computes = list()

    def setup(self):
        self.log.info('Setup Apex installer start......')
        self.key_file = self.get_ssh_key_from_installer()
        self._get_overcloud_conf()
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

    def _get_overcloud_conf(self):
        self.log.info('Get overcloud config details from Apex installer'
                      '......')

        command = "source stackrc; nova list | grep ' overcloud-'"
        raw_ips_list = self._run_cmd_remote(self.client, command)
        for line in raw_ips_list:
            ip = line.split('ctlplane=', 1)[1].split(" ", 1)[0]
            if 'overcloud-controller-' in line:
                self.controllers.append(ip)
            elif 'overcloud-novacompute-' in line:
                self.computes.append(ip)
        command = "grep docker /home/stack/deploy_command"
        self.use_containers = self._check_cmd_remote(self.client, command)
        self.log.info('controller_ips:%s' % self.controllers)
        self.log.info('compute_ips:%s' % self.computes)
        self.log.info('use_containers:%s' % self.use_containers)

    def get_host_ip_from_hostname(self, hostname):
        self.log.info('Get host ip by hostname=%s from Apex installer......'
                      % hostname)

        hostname_in_undercloud = hostname.split('.')[0]
        command = "source stackrc; nova show %s | awk '/ ctlplane network /{print $5}'" % (hostname_in_undercloud)   # noqa
        host_ips = self._run_cmd_remote(self.client, command)
        return host_ips[0]

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

        if self.use_containers:
            restart_cmd = (self._set_docker_restart_cmd(
                           "ceilometer-notification"))
            set_scripts.append(self.ac_restart_script)
        else:
            restart_cmd = 'sudo systemctl restart' \
                          ' openstack-ceilometer-notification.service'

        if self.conf.test_case != 'fault_management':
            if self.use_containers:
                restart_cmd += self._set_docker_restart_cmd("nova-scheduler")
            else:
                restart_cmd += ' openstack-nova-scheduler.service'
            set_scripts.append(self.nc_set_compute_script)

        if self.conf.inspector.type == Inspector.CONGRESS:
            if self.use_containers:
                restart_cmd += self._set_docker_restart_cmd("congress-server")
            else:
                restart_cmd += ' openstack-congress-server.service'
            set_scripts.append(self.cg_set_script)

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name,
                               key_filename=self.key_file)
            self._run_apply_patches(client,
                                    restart_cmd,
                                    set_scripts,
                                    python=self.python)
        time.sleep(5)

        self.log.info('Set apply patches start......')

        if self.conf.test_case != 'fault_management':
            if self.use_containers:
                restart_cmd = self._set_docker_restart_cmd("nova")
            else:
                restart_cmd = 'sudo systemctl restart' \
                              ' openstack-nova-compute.service'
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

        if self.use_containers:
            restart_cmd = (self._set_docker_restart_cmd(
                           "ceilometer-notification"))
            restore_scripts.append(self.ac_restore_script)
        else:
            restart_cmd = 'sudo systemctl restart' \
                          ' openstack-ceilometer-notification.service'

        if self.conf.test_case != 'fault_management':
            if self.use_containers:
                restart_cmd += self._set_docker_restart_cmd("nova-scheduler")
            else:
                restart_cmd += ' openstack-nova-scheduler.service'
            restore_scripts.append(self.nc_restore_compute_script)

        if self.conf.inspector.type == Inspector.CONGRESS:
            if self.use_containers:
                restart_cmd += self._set_docker_restart_cmd("congress-server")
            else:
                restart_cmd += ' openstack-congress-server.service'
            restore_scripts.append(self.cg_restore_script)

        for node_ip in self.controllers:
            client = SSHClient(node_ip, self.node_user_name,
                               key_filename=self.key_file)
            self._run_apply_patches(client,
                                    restart_cmd,
                                    restore_scripts,
                                    python=self.python)

        if self.conf.test_case != 'fault_management':
            if self.use_containers:
                restart_cmd = self._set_docker_restart_cmd("nova-compute")
            else:
                restart_cmd = 'sudo systemctl restart' \
                              ' openstack-nova-compute.service'
            for node_ip in self.computes:
                self._run_apply_patches(
                    client, restart_cmd,
                    [self.nc_restore_compute_script],
                    python=self.python)
