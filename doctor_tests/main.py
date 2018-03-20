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
import time

from doctor_tests import config
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.image import Image
from doctor_tests.installer import get_installer
import doctor_tests.logger as doctor_log
from doctor_tests.os_clients import nova_client
from doctor_tests.scenario.fault_management import FaultManagement
from doctor_tests.user import User


Logger = doctor_log.Logger('doctor')
LOG = Logger.getLogger()
LogFile = Logger.getLogFilename()


class DoctorTest(object):

    def __init__(self, conf):
        self.conf = conf
        self.image = Image(self.conf, LOG)
        self.user = User(self.conf, LOG)
        self.installer = get_installer(self.conf, LOG)
        auth = get_identity_auth(project=self.conf.doctor_project)
        self.nova = nova_client(self.conf.nova_version,
                                get_session(auth=auth))

    def setup(self):
        # prepare the cloud env
        self.installer.setup()

        # preparing VM image...
        self.image.create()

        # creating test user...
        self.user.create()

    def test_fault_management(self):
        try:
            LOG.info('doctor fault management test starting.......')

            self.fault_management = \
                FaultManagement(self.conf, self.installer, self.user, LOG)

            # prepare test env
            self.fault_management.setup()

            # wait for aodh alarms are updated in caches for event evaluator,
            # sleep time should be larger than event_alarm_cache_ttl
            # (default 60)
            # (tojuvone) Fraser currently needs 120
            time.sleep(120)

            # injecting host failure...
            # NOTE (umar) add INTERFACE_NAME logic to host injection
            self.fault_management.start()
            time.sleep(10)

            # verify the test results
            # NOTE (umar) copy remote monitor.log file when monitor=collectd
            self.fault_management.check_host_status('down')
            self.fault_management.check_notification_time()

        except Exception as e:
            LOG.error('doctor fault management test failed, '
                      'Exception=%s' % e)
            sys.exit(1)
        finally:
            self.fault_management.cleanup()

    def _amount_compute_nodes(self):
        services = self.nova.services.list(binary='nova-compute')
        return len(services)

    def test_maintenance(self):
        cnodes = self._amount_compute_nodes()
        if cnodes < 3:
            # need 2 compute for redundancy and one spare to migrate
            LOG.info('not enough compute nodes, skipping doctor '
                     'maintenance test')
            return
        try:
            LOG.info('doctor maintenance test starting.......')
            # TODO (tojuvone) test setup and actual test
        except Exception as e:
            LOG.error('doctor maintenance test failed, Exception=%s' % e)
            sys.exit(1)
        # TODO (tojuvone) finally: test case specific cleanup

    def run(self):
        """run doctor tests"""
        try:
            LOG.info('doctor test starting.......')
            # prepare common test env
            self.setup()
            if self.conf.test_case == 'all':
                self.test_fault_management()
                self.test_maintenance()
            else:
                function = 'test_%s' % self.conf.test_case
                if hasattr(self, function):
                    getattr(self, function)()
                else:
                    raise Exception('Can not find function <%s> in'
                                    'DoctorTest, see config manual'
                                    % function)
        except Exception as e:
            LOG.error('doctor test failed, Exception=%s' % e)
            sys.exit(1)
        finally:
            self.cleanup()

    def cleanup(self):
        self.installer.cleanup()
        self.image.delete()
        self.user.delete()


def main():
    """doctor main"""
    test_dir = os.path.split(os.path.realpath(__file__))[0]
    doctor_root_dir = os.path.dirname(test_dir)

    config_file_dir = '{0}/{1}'.format(doctor_root_dir, 'etc/')
    config_files = [join(config_file_dir, f)
                    for f in os.listdir(config_file_dir)
                    if isfile(join(config_file_dir, f))]

    conf = config.prepare_conf(args=sys.argv[1:],
                               config_files=config_files)

    doctor = DoctorTest(conf)
    doctor.run()
