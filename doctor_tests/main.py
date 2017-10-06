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
import random
import sys
import time

from doctor_tests.alarm import Alarm
from doctor_tests.common.constants import Host
from doctor_tests.common.utils import match_rep_in_file
from doctor_tests import config
from doctor_tests.consumer import get_consumer
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.image import Image
from doctor_tests.instance import Instance
from doctor_tests.inspector import get_inspector
from doctor_tests.installer import get_installer
import doctor_tests.logger as doctor_log
from doctor_tests.network import Network
from doctor_tests.monitor import get_monitor
from doctor_tests.os_clients import nova_client
from doctor_tests.profiler_poc import main as profiler_main
from doctor_tests.scenario.common import calculate_notification_time
from doctor_tests.scenario.network_failure import NetworkFault
from doctor_tests.user import User


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
                                   self.inspector.get_inspector_url(),
                                   LOG)
        self.consumer = get_consumer(self.conf, LOG)
        self.fault = NetworkFault(self.conf, self.installer, LOG)
        auth = get_identity_auth(project=self.conf.doctor_project)
        self.nova = nova_client(self.conf.nova_version,
                                get_session(auth=auth))
        self.down_host = None

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

        self.down_host = self.get_host_info_for_random_vm()
        self.monitor.start(self.down_host)

        self.consumer.start()

    def run(self):
        """run doctor test"""
        try:
            LOG.info('doctor test starting.......')

            # prepare test env
            self.setup()

            # wait for aodh alarms are updated in caches for event evaluator,
            # sleep time should be larger than event_alarm_cache_ttl(default 60)
            time.sleep(60)

            # injecting host failure...
            # NOTE (umar) add INTERFACE_NAME logic to host injection

            self.fault.start(self.down_host)
            time.sleep(10)

            # verify the test results
            # NOTE (umar) copy remote monitor.log file when monitor=collectd
            self.check_host_status(self.down_host.name, 'down')

            notification_time = calculate_notification_time(LOG.filename)
            if notification_time < 1 and notification_time > 0:
                LOG.info('doctor test successfully, notification_time=%s' % notification_time)
            else:
                LOG.error('doctor test failed, notification_time=%s' % notification_time)
                sys.exit(1)

            if self.conf.profiler_type:
                LOG.info('doctor test begin to run profile.......')
                self.collect_logs()
                self.run_profiler()
        except Exception as e:
            LOG.error('doctor test failed, Exception=%s' % e)
            sys.exit(1)
        finally:
            self.cleanup()

    def get_host_info_for_random_vm(self):
        num = random.randint(0, self.conf.instance_count - 1)
        vm_name = "%s%d" % (self.conf.instance_basename, num)

        servers = \
            {getattr(server, 'name'): server
             for server in self.nova.servers.list()}
        server = servers.get(vm_name)
        if not server:
            raise \
                Exception('Can not find instance: vm_name(%s)' % vm_name)
        host_name = server.__dict__.get('OS-EXT-SRV-ATTR:hypervisor_hostname')
        host_ip = self.installer.get_host_ip_from_hostname(host_name)

        LOG.info('Get host info(name:%s, ip:%s) which vm(%s) launched at'
                 % (host_name, host_ip, vm_name))
        return Host(host_name, host_ip)

    def check_host_status(self, hostname, state):
        service = self.nova.services.list(host=hostname, binary='nova-compute')
        host_state = service[0].__dict__.get('state')
        assert host_state == state

    def unset_forced_down_hosts(self):
        if self.down_host:
            self.nova.services.force_down(self.down_host.name, 'nova-compute', False)
            time.sleep(2)
            self.check_host_status(self.down_host.name, 'up')

    def collect_logs(self):
        self.fault.get_disable_network_log()

    def run_profiler(self):
        test_dir = os.path.split(os.path.realpath(__file__))[0]

        reg = '(?<=doctor set link down at )\d+.\d+'
        linkdown = float(match_rep_in_file(reg, LOG.filename).group(0))

        reg = '(.* doctor mark vm.* error at )(\d+.\d+)'
        vmdown = float(match_rep_in_file(reg, LOG.filename).group(2))

        reg = '(.* doctor mark host.* down at )(\d+.\d+)'
        hostdown = float(match_rep_in_file(reg, LOG.filename).group(2))

        reg = '(?<=doctor monitor detected at )\d+.\d+'
        detected = float(match_rep_in_file(reg, LOG.filename).group(0))

        reg = '(?<=doctor consumer notified at )\d+.\d+'
        notified = float(match_rep_in_file(reg, LOG.filename).group(0))

        # TODO(yujunz) check the actual delay to verify time sync status
        # expected ~1s delay from $trigger to $linkdown
        relative_start = linkdown
        os.environ['DOCTOR_PROFILER_T00'] = str(int((linkdown - relative_start)*1000))
        os.environ['DOCTOR_PROFILER_T01'] = str(int((detected - relative_start) * 1000))
        os.environ['DOCTOR_PROFILER_T03'] = str(int((vmdown - relative_start) * 1000))
        os.environ['DOCTOR_PROFILER_T04'] = str(int((hostdown - relative_start) * 1000))
        os.environ['DOCTOR_PROFILER_T09'] = str(int((notified - relative_start) * 1000))

        profiler_main(log=LOG)

    def cleanup(self):
        self.unset_forced_down_hosts()
        self.inspector.stop()
        self.monitor.stop()
        self.consumer.stop()
        self.installer.cleanup()
        self.alarm.delete()
        self.instance.delete()
        self.network.delete()
        self.image.delete()
        self.fault.cleanup()
        self.user.delete()


def main():
    """doctor main"""
    test_dir = os.path.split(os.path.realpath(__file__))[0]
    doctor_root_dir = os.path.dirname(test_dir)

    config_file_dir = '{0}/{1}'.format(doctor_root_dir, 'etc/')
    config_files = [join(config_file_dir, f) for f in os.listdir(config_file_dir)
                    if isfile(join(config_file_dir, f))]

    conf = config.prepare_conf(args=sys.argv[1:],
                               config_files=config_files)

    doctor = DoctorTest(conf)
    doctor.run()
