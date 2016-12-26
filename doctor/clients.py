##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os

from oslo_config import cfg

import ceilometerclient.client as ceilometerclient
import congressclient.v1.client as congressclient
import glanceclient.client as glanceclient
from keystoneclient.v2_0 import client as ks_client
from keystoneclient import session as ksc_session
from keystoneclient.auth.identity import v2
import novaclient.client as novaclient


OPTS = [
    cfg.StrOpt('OS_USERNAME',
               default=os.environ.get('OS_USERNAME', 'admin'),
               help='User name to use for OpenStack service access.'),
    cfg.StrOpt('OS_PASSWORD',
               secret=True,
               default=os.environ.get('OS_PASSWORD', 'stack'),
               help='Password to use for OpenStack service access.'),
    cfg.StrOpt('OS_TENANT_NAME',
               default=os.environ.get('OS_TENANT_NAME', 'admin'),
               help='Tenant name to use for OpenStack service access.'),
    cfg.StrOpt('OS_AUTH_URL',
               default=os.environ.get('OS_AUTH_URL',
                                      'http://10.62.99.239:5000/v2.0'),
               help='Auth URL to use for OpenStack service access.'),
    cfg.StrOpt('ceilometer_version', default='2', help='ceilometer version'),
    cfg.StrOpt('glance_version', default='2', help='glance version'),
    cfg.FloatOpt('nova_version', default='2.11', help='Nova version'),
]

def get_session(conf, requests_session=None):
    """Get a user credentials auth session."""

    auth = v2.Password(auth_url=conf.keystone_auth.OS_AUTH_URL,
                       username=conf.keystone_auth.OS_USERNAME,
                       password=conf.keystone_auth.OS_PASSWORD,
                       tenant_name=conf.keystone_auth.OS_TENANT_NAME)
    return ksc_session.Session(auth=auth)


def nova_client(conf):
    """Get an instance of nova client"""

    return novaclient.Client(session=get_session(conf),
                             api_version=conf.keystone_auth.nova_version)


def keystone_client(conf):
    return ks_client.Client(session=get_session(conf))
