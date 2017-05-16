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
import glanceclient.client as glanceclient


OPTS = [
    cfg.StrOpt('glance_version', default='2', help='glance version'),
    cfg.StrOpt('aodh_version', default='2', help='aodh version'),
]


def glance_client(version, session):
    return glanceclient.Client(version=version,
                               session=session)


def aodh_client(version, session):
    return aodhclient.Client(version, session=session)