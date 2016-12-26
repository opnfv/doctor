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
from keystoneclient import session as ksc_session
from keystoneclient.auth.identity import v2
import novaclient.client as novaclient


CFG_GROUP = 'SERVICE_CREDENTIALS'

OPTS = [
    cfg.StrOpt('os-username',
               default=os.environ.get('OS_USERNAME', 'admin'),
               help='User name to use for OpenStack service access.'),
    cfg.StrOpt('os-password',
               secret=True,
               default=os.environ.get('OS_PASSWORD', 'admin'),
               help='Password to use for OpenStack service access.'),
    cfg.StrOpt('os-tenant-name',
               default=os.environ.get('OS_TENANT_NAME', 'admin'),
               help='Tenant name to use for OpenStack service access.'),
    cfg.StrOpt('os-auth-url',
               default=os.environ.get('OS_AUTH_URL',
                                      'http://localhost:5000/v2.0'),
               help='Auth URL to use for OpenStack service access.'),
    cfg.StrOpt('ceilometer_version', default='2', help='ceilometer version'),
    cfg.StrOpt('glance_version', default='2', help='glance version'),    
    cfg.FloatOpt('nova_version', default='2.11', help='Nova version'),         
]


def ceilometer_client(conf):
    """Get an instance of ceilometer client"""
    return ceilometerclient.Client(conf.ceilometer_version,
                                   conf.os-username,
                                   conf.os-password,
                                   conf.os-tenant-name,
                                   conf.os-auth-url)


def nova_client(conf):
    """Get an instance of nova client"""
    return novaclient.Client(conf.nova_version,
                             conf.os-username,
                             conf.os-password,
                             conf.os-tenant-name,
                             conf.os-auth-url,
                             connection_pool=True)


def glance_client(conf):
    """Get an instance of glance client"""
    return glanceclient.Client(conf.glance_version,
                               conf.os-username,
                               conf.os-password,
                               conf.os-tenant-name,
                               conf.os-auth-url)


def congress_client(conf):
    """Get an instance of congress client"""
    auth = v2.Password(auth_url=conf.os-auth-url,
                       username=conf.os-auth-url,
                       password=conf.os-password,
                       tenant_name=conf.os-tenant-name)
    session = ksc_session.Session(auth=auth)
    return congressclient.Client(session=session, service_type='policy')


def download_image():
    pass


def upload_image_to_cloud():
    pass


def create_doctor_user():
    pass


def boot_test_vm():
    pass


def create_test_alarm():
    pass


