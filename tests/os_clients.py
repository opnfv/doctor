##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os

import ceilometerclient.client as ceilometerclient
import glanceclient.client as glanceclient
from keystoneclient import session as ksc_session
from keystoneclient.auth.identity import v2
from keystoneclient.v2_0 import client as ks_client
import novaclient.client as novaclient
from oslo_config import cfg


OPTS = [
    cfg.StrOpt('OS_USERNAME',
               default=os.environ.get('OS_USERNAME', 'admin'),
               help='User name to use for OpenStack service access.'),
    cfg.StrOpt('OS_PASSWORD',
               secret=True,
               default=os.environ.get('OS_PASSWORD', 'admin'),
               help='Password to use for OpenStack service access.'),
    cfg.StrOpt('OS_PROJECT_NAME',
               default=os.environ.get('OS_PROJECT_NAME', 'admin'),
               help='Tenant name to use for OpenStack service access.'),
    cfg.StrOpt('OS_AUTH_URL',
               default=os.environ.get('OS_AUTH_URL',
                                      'http://192.168.122.180:5000/v2.0'),
               help='Auth URL to use for OpenStack service access.'),
    cfg.StrOpt('aodh_version', default='2', help='aodh version'),
    cfg.StrOpt('glance_version', default='2', help='glance version'),
    cfg.FloatOpt('nova_version', default='2.11', help='Nova version'),
]


def get_session(conf, **kwargs):
    """Get a user credentials auth session."""

    auth_url = kwargs.pop('auth_url', conf.keystone_auth.OS_AUTH_URL)
    user_name = kwargs.pop('username', conf.keystone_auth.OS_USERNAME)
    password = kwargs.pop('password', conf.keystone_auth.OS_PASSWORD)
    project_name = kwargs.pop('project_name', conf.keystone_auth.OS_PROJECT_NAME)

    auth = v2.Password(auth_url=auth_url,
                       username=user_name,
                       password=password,
                       tenant_name=project_name)
    return ksc_session.Session(auth=auth)


def nova_client(conf, session):
    """Get an instance of nova client"""
    return novaclient.Client(conf.keystone_auth.nova_version,
                             session=session)


def keystone_client(conf, session):
    return ks_client.Client(session=session)


def ceilometer_client(conf, session):
    return ceilometerclient.get_client(
        version=conf.keystone_auth.aodh_version,
        session=session)


def glance_client(conf, session):
    return glanceclient.Client(version=conf.keystone_auth.glance_version,
                               session=session)
