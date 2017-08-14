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

from alarm import Alarm
import config
from consumer import get_consumer
from image import Image
from instance import Instance
from inspector import get_inspector
from installer import get_installer
import logger as doctor_log
from network import Network
from monitor import get_monitor
from scenario.common import calculate_notification_time
from scenario.network_failure import NetworkFault
from user import User


LOG = doctor_log.Logger('doctor').getLogger()


class DoctorTest(object):

    def __init__(self, conf):
        self.conf = conf
        self.image = Image(self.conf, LOG)
        self.user = User(self.conf, LOG)
        self.network = Network(self.conf, LOG)
        self.instance = Instance(self.conf, LOG)
        self.alarm = Alarm(self.conf, LOG)
        self.installer = get_installer(self.conf, LOG)
        self.inspector = get_inspector(self.conf, LOG)
        self.monitor = get_monitor(self.conf,
                                   self.installer,
                                   self.inspector.get_inspector_url(),
                                   LOG)
        self.consumer = get_consumer(self.conf, LOG)
        self.fault = NetworkFault(self.conf, self.installer, LOG)

    def setup(self):
        # prepare the cloud env
        self.installer.setup()

        # preparing VM image...
        self.image.create()

        # creating test user...
        self.user.create()
        self.user.update_quota()

        # creating VM...
        self.network.create()
        self.instance.create()
        self.instance.wait_for_vm_launch()

        # creating alarm...
        self.alarm.create()

        # starting doctor sample components...
        self.inspector.start()
        self.monitor.start()
        self.consumer.start()

    def run(self):
        """run doctor test"""
        try:
            LOG.info('doctor test starting.......')

            self.setup()

            # injecting host failure...
            # NOTE (umar) add INTERFACE_NAME logic to host injection
            self.fault.start()

            # verify the test results
            # NOTE (umar) copy remote monitor.log file when monitor=collectd

            self.fault.check_host_status('down')
            notification_time = calculate_notification_time()
            if notification_time < 1 and notification_time > 0:
                LOG.info('doctor test successfully, notification_time=%d' % notification_time)
            else:
                LOG.error('doctor test failed, notification_time=%d' % notification_time)
                sys.exit(1)
        except Exception as e:
            LOG.error('doctor test failed, Exception=%s' % e)
            sys.exit(1)
        finally:
            self.cleanup()

    def cleanup(self):
        self.alarm.delete()
        self.instance.delete()
        self.network.delete()
        self.image.delete()
        self.user.delete()
        self.fault.cleanup()
        self.inspector.stop()
        self.monitor.stop()
        self.consumer.stop()
        self.installer.cleanup()


def main():
    """doctor main"""
    doctor_root_dir = os.path.dirname(sys.path[0])
    config_file_dir = '{0}/{1}'.format(doctor_root_dir, 'etc/')
    config_files = [join(config_file_dir, f) for f in os.listdir(config_file_dir)
                    if isfile(join(config_file_dir, f))]

    conf = config.prepare_conf(args=sys.argv[1:],
                               config_files=config_files)

    doctor = DoctorTest(conf)
    doctor.run()


if __name__ == '__main__':
    sys.exit(main())
