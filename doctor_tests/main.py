##############################################################################
# Copyright (c) 2019 ZTE Corporation and others.
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
from traceback import format_exc

from doctor_tests import config
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.image import Image
from doctor_tests.installer import get_installer
import doctor_tests.logger as doctor_log
from doctor_tests.scenario.fault_management import FaultManagement
from doctor_tests.os_clients import nova_client
from doctor_tests.scenario.maintenance import Maintenance
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
        retry = 2
        # Retry once if notified_time is None
        while retry > 0:
            try:
                self.fault_management = None
                LOG.info('doctor fault management test starting.......')
                transport_url = self.installer.get_transport_url()
                self.fault_management = \
                    FaultManagement(self.conf, self.installer, self.user, LOG,
                                    transport_url)

                # prepare test env
                self.fault_management.setup()

                # wait for aodh alarms are updated in caches for event
                # evaluator,
                # sleep time should be larger than event_alarm_cache_ttl
                # (default 60)
                # (tojuvone) Fraser currently needs 120
                time.sleep(120)

                # injecting host failure...
                # NOTE (umar) add INTERFACE_NAME logic to host injection
                self.fault_management.start()
                time.sleep(30)

                # verify the test results
                # NOTE (umar) copy remote monitor.log file when
                # monitor=collectd
                self.fault_management.check_host_status('down')
                self.fault_management.check_notification_time()
                retry = 0

            except Exception as e:
                if 'notified_time=None' in e:
                    retry -= 1
                else:
                    retry = 0
                LOG.error('doctor fault management test failed, '
                          'Exception=%s' % e)
                LOG.error(format_exc())
                sys.exit(1)
            finally:
                if self.fault_management is not None:
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
        elif self.conf.installer.type not in ['apex', 'fuel', 'devstack']:
            LOG.info('not supported installer, skipping doctor '
                     'maintenance test')
            return
        try:
            maintenance = None
            LOG.info('doctor maintenance test starting.......')
            trasport_url = self.installer.get_transport_url()
            maintenance = Maintenance(trasport_url, self.conf, LOG)
            maintenance.setup_maintenance(self.user)

            # wait for aodh alarms are updated in caches for event evaluator,
            # sleep time should be larger than event_alarm_cache_ttl
            # (default 60)
            LOG.info('wait aodh for 120s.......')
            time.sleep(120)

            session_id = maintenance.start_maintenance()
            maintenance.wait_maintenance_complete(session_id)

            LOG.info('doctor maintenance complete.......')

        except Exception as e:
            LOG.error('doctor maintenance test failed, Exception=%s' % e)
            LOG.error(format_exc())
            sys.exit(1)
        finally:
            if maintenance is not None:
                maintenance.cleanup_maintenance()

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
            LOG.error(format_exc())
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
