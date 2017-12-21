##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from oslo_config import cfg

from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import neutron_client


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


class Network(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self.auth = get_identity_auth(username=self.conf.doctor_user,
                                      password=self.conf.doctor_passwd,
                                      project=self.conf.doctor_project)
        self.neutron = neutron_client(get_session(auth=self.auth))
        self.net = None
        self.subnet = None

    def create(self):
        self.log.info('network create start.......')
        net_name = self.conf.net_name
        networks = self.neutron.list_networks(name=net_name)['networks']
        self.net = networks[0] if networks \
            else self.neutron.create_network(
            {'network': {'name': net_name}})['network']
        self.log.info('network create end.......')

        self.log.info('subnet create start.......')
        subnets = \
            self.neutron.list_subnets(network_id=self.net['id'])['subnets']
        subnet_param = {'name': net_name, 'network_id': self.net['id'],
                        'cidr': self.conf.net_cidr, 'ip_version': 4,
                        'enable_dhcp': False}
        self.subnet = subnets[0] if subnets \
            else self.neutron.create_subnet(
            {'subnet': subnet_param})['subnet']
        self.log.info('subnet create end.......')

    def delete(self):
        self.log.info('subnet delete start.......')
        if self.subnet:
            self.neutron.delete_subnet(self.subnet['id'])
        self.log.info('subnet delete end.......')

        self.log.info('network delete start.......')
        if self.net:
            self.neutron.delete_network(self.net['id'])
        self.log.info('network delete end.......')
