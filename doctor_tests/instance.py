##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
# test
##############################################################################
import os
import time

from oslo_config import cfg

from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import neutron_client
from doctor_tests.os_clients import nova_client

OPTS = [
    cfg.StrOpt('flavor',
               default='m1.tiny',
               help='the name of flavor',
               required=True),
    cfg.IntOpt('instance_count',
               default=os.environ.get('VM_COUNT', 1),
               help='the count of instance',
               required=True),
    cfg.StrOpt('instance_basename',
               default='doctor_vm',
               help='the base name of instance',
               required=True),
]


class Instance(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self.auth = get_identity_auth(username=self.conf.doctor_user,
                                      password=self.conf.doctor_passwd,
                                      project=self.conf.doctor_project)
        self.nova = \
            nova_client(conf.nova_version,
                        get_session(auth=self.auth))
        self.neutron = neutron_client(get_session(auth=self.auth))
        self.servers = {}
        self.vm_names = []

    def create(self):
        self.log.info('instance create start......')

        # get flavor, image and network for vm boot
        flavors = {flavor.name: flavor for flavor in self.nova.flavors.list()}
        flavor = flavors.get(self.conf.flavor)
        image = self.nova.glance.find_image(self.conf.image_name)
        network = \
            self.neutron.list_networks(name=self.conf.net_name)['networks'][0]
        nics = {'net-id': network['id']}

        self.servers = \
            {getattr(server, 'name'): server
             for server in self.nova.servers.list()}
        for i in range(0, self.conf.instance_count):
            vm_name = "%s%d" % (self.conf.instance_basename, i)
            self.vm_names.append(vm_name)
            if vm_name not in self.servers:
                server = self.nova.servers.create(vm_name, image,
                                                  flavor, nics=[nics])
                self.servers[vm_name] = server
                time.sleep(0.1)

        self.log.info('instance create end......')

    def delete(self):
        self.log.info('instance delete start.......')

        for vm_name in self.vm_names:
            if vm_name in self.servers:
                self.nova.servers.delete(self.servers[vm_name])
                time.sleep(0.1)

        # check that all vms are deleted
        while self.nova.servers.list():
            time.sleep(0.1)
        self.servers.clear()
        del self.vm_names[:]

        self.log.info('instance delete end.......')

    def wait_for_vm_launch(self):
        self.log.info('wait for vm launch start......')

        wait_time = 60
        count = 0
        while count < wait_time:
            active_count = 0
            for vm_name in self.vm_names:
                server = self.nova.servers.get(self.servers[vm_name])
                server_status = getattr(server, 'status').lower()
                if 'active' == server_status:
                    active_count += 1
                elif 'error' == server_status:
                    raise Exception('vm launched with error state')
                else:
                    time.sleep(2)
                    count += 1
                    continue
            if active_count == self.conf.instance_count:
                self.log.info('wait for vm launch end......')
                return
            count += 1
            time.sleep(2)
        raise Exception('time out for vm launch')
