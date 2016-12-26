##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import doctor.doctor_test_refactor.clients
import doctor.doctor_test_refactor.consumer
import doctor.doctor_test_refactor.monitor
import doctor.doctor_test_refactor.inspector
import doctor.doctor_test_refactor.installer


def list_opts():
    return [
        ('MONITOR', doctor.doctor_test_refactor.monitor.OPTS),
        ('INSPECTOR', doctor.doctor_test_refactor.inspector.OPTS),
        ('CONSUMER', doctor.doctor_test_refactor.consumer.OPTS),
        ('INSTALLER', doctor.doctor_test_refactor.installer.OPTS),
        ('SERVICE_CREDENTIALS', doctor.doctor_test_refactor.clients.OPTS),
        ('DOCTOR_CREDENTIALS', doctor.doctor_test_refactor.service.OPTS),
    ]

