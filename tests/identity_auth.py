##############################################################################
# Copyright (c) 2017 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os

from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1 import session


def get_identity_auth(username=None, password=None, project=None):
    auth_url = os.environ['OS_AUTH_URL']
    username = username if username else os.environ['OS_USERNAME']
    password = password if password else os.environ['OS_PASSWORD']
    user_domain_name = os.environ.get('OS_USER_DOMAIN_NAME')
    project_name = project if project \
        else os.environ.get('OS_PROJECT_NAME') \
             or os.environ.get('OS_TENANT_NAME')
    project_domain_name = os.environ.get('OS_PROJECT_DOMAIN_NAME')
    if auth_url.endswith('v3'):
        return v3.Password(auth_url=auth_url,
                           username=username,
                           password=password,
                           user_domain_name=user_domain_name,
                           project_name=project_name,
                           project_domain_name=project_domain_name)
    else:
        return v2.Password(auth_url=auth_url,
                           username=username,
                           password=password,
                           tenant_name=project_name)


def get_session(auth=None):
    """Get a user credentials auth session."""
    if auth is None:
        auth = get_identity_auth()
    return session.Session(auth=auth)
