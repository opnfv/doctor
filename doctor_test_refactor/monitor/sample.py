##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from doctor.doctor_test_refactor.monitor.base import Monitor


class SampleMonitor(Monitor):

    def __init__(self, conf):
        super(SampleMonitor, self).__init__(conf)

    def start(self):
        pass
