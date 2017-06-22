##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
from os.path import isfile, join
import sys

import config
from image import Image
import logger as doctor_log
from user import User


LOG = doctor_log.Logger('doctor').getLogger()


class DoctorTest(object):

    def __init__(self, conf):
        self.conf = conf
        self.image = Image(self.conf, LOG)
        self.user = User(self.conf, LOG)

    def setup(self):
        # prepare the cloud env

        # preparing VM image...
        self.image.create()

        # creating test user...
        self.user.create()
        self.user.update_quota()

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


def main():
    """doctor main"""
    doctor_root_dir = os.path.dirname(os.getcwd())
    config_file_dir = '{0}/{1}'.format(doctor_root_dir, 'etc/')
    config_files = [f for f in os.listdir(config_file_dir)
                    if isfile(join(config_file_dir, f))]

    conf = config.prepare_conf(args=sys.argv[1:],
                               config_files=config_files)

    doctor = DoctorTest(conf)
    doctor.run()


if __name__ == '__main__':
    sys.exit(main())
