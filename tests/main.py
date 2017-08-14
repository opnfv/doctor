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

from alarm import Alarm
from common.constants import Host
import config
from consumer import get_consumer
from identity_auth import get_identity_auth
from identity_auth import get_session
from image import Image
from instance import Instance
from inspector import get_inspector
from installer import get_installer
import logger as doctor_log
from network import Network
from monitor import get_monitor
from os_clients import nova_client
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

            self.setup()

            # injecting host failure...
            # NOTE (umar) add INTERFACE_NAME logic to host injection
            self.fault.start(self.down_host)
            time.sleep(10)

            # verify the test results
            # NOTE (umar) copy remote monitor.log file when monitor=collectd
            self.check_host_status(self.down_host, 'down')

            notification_time = calculate_notification_time()
            if notification_time < 1 and notification_time > 0:
                LOG.info('doctor test successfully, notification_time=%s' % notification_time)
            else:
                LOG.error('doctor test failed, notification_time=%s' % notification_time)
                sys.exit(1)
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

    def check_host_status(self, host, state):
        service = self.nova.services.list(host=host.name, binary='nova-compute')
        host_state = service[0].__dict__.get('state')
        assert host_state == state

    def cleanup(self):
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
