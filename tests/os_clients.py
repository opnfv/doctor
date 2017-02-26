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
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v2_0 import client as ks_client
import novaclient.client as novaclient
from oslo_config import cfg


OPTS = [
    cfg.StrOpt('username',
               default=os.environ.get('OS_USERNAME'),
               help='User name to use for OpenStack service access.'),
    cfg.StrOpt('password',
               secret=True,
               default=os.environ.get('OS_PASSWORD'),
               help='Password to use for OpenStack service access.'),
    cfg.StrOpt('project_name',
               default=os.environ.get('OS_PROJECT_NAME', os.environ.get('OS_TENANT_NAME')),
               help='Tenant name to use for OpenStack service access.'),
    cfg.StrOpt('auth_url',
               default=os.environ.get('OS_AUTH_URL'),
               help='Auth URL to use for OpenStack service access.'),
    cfg.StrOpt('domain_name',
               default=os.environ.get('OS_USER_DOMAIN_NAME'),
               help='Domain name to use for OpenStack service access.'),
    cfg.StrOpt('project_domain_name',
               default=os.environ.get('OS_PROJECT_DOMAIN_NAME'),
               help='Project domain name to use for OpenStack service access.'),
    cfg.StrOpt('aodh_version', default='2', help='aodh version'),
    cfg.StrOpt('glance_version', default='2', help='glance version'),
    cfg.FloatOpt('nova_version', default='2.34', help='Nova version'),
]


def get_session(conf, **kwargs):
    """Get a user credentials auth session."""

    auth_url = kwargs.pop('auth_url', conf.keystone_auth.auth_url)
    user_name = kwargs.pop('username', conf.keystone_auth.username)
    password = kwargs.pop('password', conf.keystone_auth.password)
    project_name = kwargs.pop('project_name', conf.keystone_auth.project_name)
    user_domain_name = kwargs.pop('user_domain_name',
                                  conf.keystone_auth.domain_name)
    project_domain_name = kwargs.pop('project_domain_name',
                                     conf.keystone_auth.project_domain_name)
    if auth_url.endswith('v3'):
        auth = v3.Password(auth_url=auth_url,
                           username=user_name,
                           password=password,
                           user_domain_name=user_domain_name,
                           project_name=project_name,
                           project_domain_name=project_domain_name)
    else:
        auth = v2.Password(auth_url=auth_url,
                           username=user_name,
                           password=password,
                           tenant_name=project_name)

    return session.Session(auth=auth)



def nova_client(conf, session):
    """Get an instance of nova client"""
    return novaclient.Client(conf.keystone_auth.nova_version,
                             session=session,
                             connection_pool=True)


def keystone_client(conf, session):
    return ks_client.Client(session=session)


def ceilometer_client(conf, session):
    return ceilometerclient.get_client(
        version=conf.keystone_auth.aodh_version,
        session=session)


def glance_client(conf, session):
    return glanceclient.Client(version=conf.keystone_auth.glance_version,
                               session=session)
