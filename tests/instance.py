##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import time

from oslo_config import cfg

from identity_auth import get_identity_auth
from identity_auth import get_session
from os_clients import neutron_client
from os_clients import nova_client
import logger as doctor_log

OPTS = [
    cfg.StrOpt('flavor',
               default='m1.tiny',
               help='the name of flavor',
               required=True),
    cfg.StrOpt('vm_basename',
               default='doctor_vm',
               help='the base name of instance',
               required=True),
]

LOG = doctor_log.Logger('doctor').getLogger()


class Instance(object):

    def __init__(self, conf):
        self.conf = conf
        self.auth = get_identity_auth(username=self.conf.user,
                                      password=self.conf.password,
                                      project=self.conf.project_name)
        self.nova = \
            nova_client(conf.nova_version,
                        get_session(auth=self.auth))
        self.neutron = neutron_client(get_session(auth=self.auth))
        self.servers = {}
        self.vm_names = []

    def create(self):
        LOG.info('instance create start......')

        # get flavor, image and network for vm boot
        flavors = {flavor.name: flavor for flavor in self.nova.flavors.list()}
        flavor = flavors.get(self.conf.flavor)
        image = self.nova.glance.find_image(self.conf.image.name)
        network = self.neutron.list_networks(name=self.conf.net_name)['networks'][0]
        nics = {'net-id': network['id']}

        self.servers = \
            {server.name: server for server in self.nova.servers.list()}
        for i in range(0, self.conf.vm_count):
            vm_name = "%s%d"%(self.conf.vm_basename, i)
            self.vm_names.append(vm_name)
            if vm_name not in self.servers:
                server = self.nova.servers.create(vm_name, image,
                                                  flavor, nics=[nics])
                self.servers[vm_name] = server
                time.sleep(0.1)

        LOG.info('instance create end......')

    def delete(self):
        LOG.info('instance delete start.......')

        for vm_name in self.vm_names:
            if vm_name in self.servers:
                self.nova.servers.delete(self.servers[vm_name])

        LOG.info('instance delete end.......')

    def wait_for_vm_launch(self):
        LOG.info('wait for vm launch start......')

        wait_time = 60
        count = 0
        while count < wait_time:
            active_count = 0
            for vm_name in self.vm_names:
                server = self.servers[vm_name]
                if 'active' == server.__dict__.get('state'):
                    active_count += 1
                elif 'error' == server.__dict__.get('state'):
                    raise Exception('vm launched with error state')
                else:
                    time.sleep(5)
                    count += 1
                    continue
            if active_count == self.conf.vm_count:
                LOG.info('wait for vm launch end......')
                return
            count += 1
            time.sleep(5)
        raise Exception('time out for vm launch')

