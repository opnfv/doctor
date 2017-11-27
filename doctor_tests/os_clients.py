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
from keystoneclient.v2_0 import client as ks_client
from neutronclient.v2_0 import client as neutronclient
import novaclient.client as novaclient
import vitrageclient.client as vitrageclient


OPTS = [
    cfg.StrOpt('glance_version', default='2', help='glance version'),
    cfg.StrOpt('nova_version', default='2.34', help='Nova version'),
    cfg.StrOpt('aodh_version', default='2', help='aodh version'),
    cfg.StrOpt('vitrage_version', default='1', help='vitrage version'),
]


def glance_client(version, session):
    return glanceclient.Client(version=version,
                               session=session)


def keystone_client(session):
    return ks_client.Client(session=session)


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


def vitrage_client(version, session):
    return vitrageclient.Client(version=version,
                                session=session)
