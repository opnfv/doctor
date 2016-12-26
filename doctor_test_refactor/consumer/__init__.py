##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from oslo_config import cfg


OPTS = [
    cfg.StrOpt('consumer',
               default='sample',
               help='the component of doctor consumer',
               required=True),
    cfg.StrOpt('consumer_ip',
               default='',
               help='the ip of consumer'),
    cfg.IntOpt('consumer_port',
               default='12346',
               help='the port of doctor consumer',
               required=True),  
]