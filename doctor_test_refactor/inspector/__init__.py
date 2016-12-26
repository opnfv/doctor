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


OPTS = [
    cfg.StrOpt('inspector_type',
               default=os.environ.get('INSPECTOR_TYPE', 'sample'),
               help='the component of doctor inspector',
               required=True),
]
