##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import random
import os
import stat

from identity_auth import get_identity_auth
from identity_auth import get_session
from os_clients import nova_client
from utils import SSHClient


class NetworkFault(object):

    def __init__(self, conf, installer, log):
        self.conf = conf
        self.log = log
        self.installer = installer
        self.downed_computes = {}
        self.ssh_clients = list()

    def start(self):
        self.inject_failure()

    def cleanup(self):
        nova = nova_client(self.conf.nova_version,
                           get_session())
        for hostname in self.downed_computes.keys():
            nova.services.force_down(hostname, 'nova-compute', False)

        for client in self.ssh_clients:
            client.scp('disable_network.log', './disable_network.log', method='get')

    def inject_failure(self):
        # find a compute host which a test vm is launched at
        compute_name = self._pick_compute_from_random_vm()
        compute_ip = self.installer.get_compute_ip_from_hostname(compute_name)
        self.downed_computes[compute_name] = compute_ip
        self._write_disable_network_file(compute_ip)
        self._set_link_down(compute_ip)

    def check_host_status(self, status):
        pass

    def _pick_compute_from_random_vm(self):
        auth = get_identity_auth(username=self.conf.doctor_user,
                                 password=self.conf.doctor_passwd,
                                 project=self.conf.doctor_project)
        nova = nova_client(self.conf.nova_version,
                           get_session(auth=auth))
        servers = \
            {getattr(server, 'name'): server
             for server in nova.servers.list()}
        num = random.randint(0, self.conf.instance_count-1)
        vm_name = "%s%d" % (self.conf.instance_basename, num)
        server = servers.get(vm_name)
        if not server:
            raise \
                Exception('Can not find instance under doctor project: vm_name(%s)' % vm_name)
        return server.__dict__.get('OS-EXT-SRV-ATTR:host')

    def _write_disable_network_file(self, computer_ip):
        template = """#!/bin/bash -x
dev=$(sudo ip a | awk '/ {computer_ip}\//{{print $NF}}')
sleep 1
sudo ip link set $dev down
echo "doctor set link down at" $(date "+%s.%N")
sleep 10
sudo ip link set $dev up
sleep 1
        """
        file_name = './disable_network.sh'
        with open(file_name, 'w') as file:
            file.write(template.format(computer_ip=computer_ip))
        os.chmod('./disable_network.sh', stat.S_IXUSR)

    def _set_link_down(self, compute_ip):
        client = SSHClient(compute_ip,
                           self.installer.computer_user_name,
                           key_filename=self.installer.get_ssh_key_file())
        self.ssh_clients.append(client)
        client.scp('./disable_network.sh', 'disable_network.sh')
        command = 'nohup bash disable_network.sh > disable_network.log 2>&1 &'
        client.ssh(command)
