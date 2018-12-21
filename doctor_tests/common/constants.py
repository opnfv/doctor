##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from collections import namedtuple


Host = namedtuple('Host', ['name', 'ip'])


def is_fenix(conf):
    return conf.admin_tool.type == 'fenix'


class Inspector(object):
    CONGRESS = 'congress'
    SAMPLE = 'sample'
    VITRAGE = 'vitrage'
