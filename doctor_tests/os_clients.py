##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from oslo_config import cfg

import aodhclient.client as aodhclient
from congressclient.v1 import client as congressclient
import glanceclient.client as glanceclient
import heatclient.client as heatclient
from keystoneclient import client as ks_client
from neutronclient.v2_0 import client as neutronclient
import novaclient.client as novaclient


OPTS = [
    cfg.StrOpt('glance_version', default='2', help='glance version'),
    cfg.StrOpt('nova_version', default='2.34', help='Nova version'),
    cfg.StrOpt('aodh_version', default='2', help='aodh version'),
    cfg.StrOpt('vitrage_version', default='1', help='vitrage version'),
    cfg.StrOpt('keystone_version', default='v3', help='keystone version'),
    cfg.StrOpt('heat_version', default='1', help='heat version'),
]


def glance_client(version, session):
    return glanceclient.Client(version=version,
                               session=session)


def heat_clientm(version, endpoint, token):
    return heatclient.Client(version, endpoint, token)


def heat_client(version, session):
    return heatclient.Client(version=version,
                             session=session)


def keystone_client(version, session):
    return ks_client.Client(version=version,
                            session=session)


def nova_client(version, session):
    return novaclient.Client(version=version,
                             session=session)


def neutron_client(session):
    return neutronclient.Client(session=session)


def aodh_client(version, session):
    return aodhclient.Client(version, session=session)


def congress_client(session):
    return congressclient.Client(session=session,
                                 service_type='policy')
