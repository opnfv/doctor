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
from inspector import get_inspector
import logger as doctor_log
from user import User
from monitor import get_monitor


LOG = doctor_log.Logger('doctor').getLogger()


class DoctorTest(object):

    def __init__(self, conf):
        self.conf = conf
        self.image = Image(self.conf, LOG)
        self.user = User(self.conf, LOG)
        self.inspector = get_inspector(self.conf, LOG)
        self.monitor = get_monitor(self.conf,
                                   self.inspector.get_inspector_url(),
                                   LOG)

    def setup(self):
        # prepare the cloud env

        # preparing VM image...
        self.image.create()

        # creating test user...
        self.user.create()
        self.user.update_quota()

        # starting doctor sample components...
        self.inspector.start()
        self.monitor.start()

    def run(self):
        """run doctor test"""
        try:
            LOG.info('doctor test starting.......')

            self.setup()

            # injecting host failure...

            # verify the test results

        except Exception as e:
            LOG.error('doctor test failed, Exception=%s' % e)
            sys.exit(1)
        finally:
            self.cleanup()

    def cleanup(self):
        self.image.delete()
        self.user.delete()
        self.inspector.stop()
        self.monitor.stop()


def main():
    """doctor main"""
    conf = config.prepare_conf()

    doctor = DoctorTest(conf)
    doctor.run()


if __name__ == '__main__':
    sys.exit(main())
