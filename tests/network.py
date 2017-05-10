##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from oslo_config import cfg

from identity_auth import get_identity_auth
from identity_auth import get_session
from os_clients import neutron_client

import logger as doctor_log

OPTS = [
    cfg.StrOpt('net_name',
               default='doctor_net',
               help='the name of test net',
               required=True),
    cfg.StrOpt('net_cidr',
               default='192.168.168.0/24',
               help='the cidr of test subnet',
               required=True),
]

LOG = doctor_log.Logger('doctor').getLogger()


class Network(object):

    def __init__(self, conf):
        self.conf = conf
        self.auth = get_identity_auth(username=self.conf.user,
                                      password=self.conf.password,
                                      project=self.conf.project_name)
        self.neutron = neutron_client(get_session(auth=self.auth))
        self.net = None
        self.subnet = None

    def create(self):
        LOG.info('network create start.......')
        net_name = self.conf.net_name
        networks = self.neutron.list_networks(name=net_name)['networks']
        self.net = networks[0] if networks \
            else self.neutron.create_network(
            {'network': {'name': net_name}})['network']
        LOG.info('network create end.......')

        LOG.info('subnet create start.......')
        subnets = self.neutron.list_subnets(network_id=self.net['id'])['subnets']
        subnet_param = {'name': net_name, 'network_id': self.net['id'],
                        'cidr': self.conf.net_cidr, 'ip_version': 4,
                        'enable_dhcp': False}
        self.subnet = subnets[0] if subnets \
            else self.neutron.create_subnet(
            {'subnet': subnet_param})['subnet']
        LOG.info('subnet create end.......')

    def delete(self):
        LOG.info('subnet delete start.......')
        if self.subnet:
            self.neutron.delete_subnet(self.subnet['id'])
        LOG.info('subnet delete end.......')

        LOG.info('network delete start.......')
        if self.net:
            self.neutron.delete_network(self.net['id'])
        LOG.info('network delete end.......')
