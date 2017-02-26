##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import sys

import config
from image import Image
import logger as doctor_log


LOG = doctor_log.Logger(__name__).getLogger()


class DoctorTest(object):

    def __init__(self, conf):
        self.conf = conf
        self.image = Image(self.conf)

    def run(self):
        """run doctor test"""
        try:
            LOG.info('doctor test starting.......')
            # prepare the cloud env

            # preparing VM image...
            self.image.create()

            # creating test user...

            # creating VM...

            # creating alarm...

            # starting doctor sample components...

            # injecting host failure...

            # verify the test results
        except Exception as e:
            LOG.error('doctor test failed: %s ', e)
            self.image.delete()


def main():
    """doctor main"""
    conf = config.prepare_conf()

    doctor = DoctorTest(conf)
    doctor.run()


if __name__ == '__main__':
    sys.exit(main())
