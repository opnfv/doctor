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
from keystoneauth1 import loading as ka_loading
from keystoneclient import session as ksc_session
from keystoneclient.auth.identity import v2
import novaclient.client as novaclient


OPTS = [
    cfg.StrOpt('username',
               default=os.environ.get('OS_USERNAME', 'admin'),
               help='User name to use for OpenStack service access.'),
    cfg.StrOpt('password',
               secret=True,
               default=os.environ.get('OS_PASSWORD', 'stack'),
               help='Password to use for OpenStack service access.'),
    cfg.StrOpt('tenant_name',
               default=os.environ.get('OS_TENANT_NAME', 'admin'),
               help='Tenant name to use for OpenStack service access.'),
    cfg.StrOpt('auth_url',
               default=os.environ.get('OS_AUTH_URL',
                                      'http://10.62.99.239:5000/v2.0'),
               help='Auth URL to use for OpenStack service access.'),
]

CFG_GROUP = "keystone_authtoken"


def get_session(conf, requests_session=None):
    """Get a user credentials auth session."""
    auth_plugin = ka_loading.load_auth_from_conf_options(conf, CFG_GROUP)
    session = ka_loading.load_session_from_conf_options(
        conf, CFG_GROUP, auth=auth_plugin, session=requests_session
    )
    return session


def register_keystoneauth_opts(conf):
    ka_loading.register_auth_conf_options(conf, CFG_GROUP)
    ka_loading.register_session_conf_options(conf, CFG_GROUP)
    conf.set_default("auth_type", default="password",
                     group=CFG_GROUP)

def nova_client(conf):
    """Get an instance of nova client"""
    # return novaclient.Client(version=conf.CFG_GROUP.nova_version,
    #                          session=get_session(conf))
    return novaclient.Client(version=conf.nova_version,
                             username=conf.keystone_authtoken.username,
                             password=conf.keystone_authtoken.password,
                             project_id=conf.keystone_authtoken.tenant_name,
                             auth_url=conf.keystone_authtoken.auth_url)






