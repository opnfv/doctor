##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import doctor.clients
import doctor.consumer
import doctor.monitor
import doctor.inspector
import doctor.installer


def list_opts():
    return [
        ('monitor', doctor.monitor.OPTS),
        ('inspector', doctor.inspector.OPTS),
        ('consumer', doctor.consumer.OPTS),
        ('installer', doctor.installer.OPTS),
        ('keystone_authtoken', doctor.clients.OPTS),
        ('DEFAULT', doctor.service.OPTS),
    ]

