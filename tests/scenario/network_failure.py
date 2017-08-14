##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from identity_auth import get_session
from os_clients import nova_client
from common.utils import SSHClient

LINK_DOWN_SCRIPT = """
#!/bin/bash -x
dev=$(sudo ip a | awk '/ {compute_ip}\//{{print $NF}}')
sleep 1
sudo ip link set $dev down
echo "doctor set link down at" $(date "+%s.%N")
sleep 10
sudo ip link set $dev up
sleep 1
"""


class NetworkFault(object):

    def __init__(self, conf, installer, log):
        self.conf = conf
        self.log = log
        self.installer = installer
        self.nova = nova_client(self.conf.nova_version, get_session())
        self.host = None

    def start(self, host):
        self.log.info('fault inject start......')
        self._set_link_down(host.ip)
        self.log.info('fault inject end......')

    def cleanup(self):
        self.log.info('fault inject cleanup......')
        if self.host is not None:
            client = SSHClient(self.host.ip,
                               self.installer.node_user_name,
                               key_filename=self.installer.get_ssh_key_from_installer(),
                               look_for_keys=True,
                               log=self.log)
            client.scp('disable_network.log', './disable_network.log', method='get')

    def _set_link_down(self, compute_ip):
        file_name = './disable_network.sh'
        with open(file_name, 'w') as file:
            file.write(LINK_DOWN_SCRIPT.format(compute_ip=compute_ip))
        client = SSHClient(compute_ip,
                           self.installer.node_user_name,
                           key_filename=self.installer.get_ssh_key_from_installer(),
                           look_for_keys=True,
                           log=self.log)
        client.scp('./disable_network.sh', 'disable_network.sh')
        command = 'bash disable_network.sh > disable_network.log 2>&1 &'
        client.ssh(command)
