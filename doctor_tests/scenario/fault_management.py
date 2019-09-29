##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import random
import time

from doctor_tests.alarm import Alarm
from doctor_tests.common.constants import Host
from doctor_tests.common.utils import get_doctor_test_root_dir
from doctor_tests.common.utils import match_rep_in_file
from doctor_tests.common.utils import SSHClient
from doctor_tests.consumer import get_consumer
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.instance import Instance
from doctor_tests.inspector import get_inspector
from doctor_tests.monitor import get_monitor
from doctor_tests.network import Network
from doctor_tests.profiler_poc import main as profiler_main
from doctor_tests.os_clients import nova_client


LINK_DOWN_SCRIPT = """
#!/bin/bash -x
dev=$(sudo ip a | awk '/ {compute_ip}\//{{print $NF}}')
sleep 1
sudo ip link set $dev down
echo "doctor set link down at" $(date "+%s.%N")
sleep 30
sudo ip link set $dev up
sleep 1
"""


class FaultManagement(object):

    def __init__(self, conf, installer, user, log, transport_url):
        self.conf = conf
        self.log = log
        self.user = user
        self.installer = installer
        auth = get_identity_auth(project=self.conf.doctor_project)
        self.nova = nova_client(self.conf.nova_version,
                                get_session(auth=auth))
        self.test_dir = get_doctor_test_root_dir()
        self.down_host = None
        self.GetLog = False
        self.disable_network_log = None
        self.network = Network(self.conf, log)
        self.instance = Instance(self.conf, log)
        self.alarm = Alarm(self.conf, log)
        self.inspector = get_inspector(self.conf, log, transport_url)
        self.monitor = get_monitor(self.conf,
                                   self.inspector.get_inspector_url(),
                                   log)
        self.consumer = get_consumer(self.conf, log)

    def setup(self):
        self.log.info('fault management setup......')

        # user settings...
        self.user.update_quota()

        # creating VM...
        self.network.create()
        self.instance.create()
        self.instance.wait_for_vm_launch()

        # creating alarm...
        self.alarm.create()

        # starting doctor sample components...
        # tbd tojuvone: move inspector and consumer to common setup
        # when they support updating VMs via instance.create and
        # instance.delete alarm

        self.inspector.start()
        self.consumer.start()
        self.down_host = self.get_host_info_for_random_vm()
        self.monitor.start(self.down_host)

    def start(self):
        self.log.info('fault management start......')
        self._set_link_down(self.down_host.ip)
        self.log.info('fault management end......')

    def cleanup(self):
        self.log.info('fault management cleanup......')

        self.get_disable_network_log()
        self.unset_forced_down_hosts()
        self.inspector.stop()
        self.monitor.stop()
        self.consumer.stop()
        self.alarm.delete()
        self.instance.delete()
        self.network.delete()

    def get_host_info_for_random_vm(self):
        num = random.randint(0, self.conf.instance_count - 1)
        vm_name = "%s%d" % (self.conf.instance_basename, num)

        servers = {getattr(server, 'name'): server
                   for server in self.nova.servers.list()}
        server = servers.get(vm_name)
        if not server:
            raise Exception('Can not find instance: vm_name(%s)' % vm_name)
        # use hostname without domain name which is mapped to the cell
        host_name = server.__dict__.get('OS-EXT-SRV-ATTR:hypervisor_hostname').split('.')[0]
        host_ip = self.installer.get_host_ip_from_hostname(host_name)

        self.log.info('Get host info(name:%s, ip:%s) which vm(%s) launched at'
                      % (host_name, host_ip, vm_name))
        return Host(host_name, host_ip)

    def unset_forced_down_hosts(self):
        if self.down_host:
            self.nova.services.force_down(self.down_host.name,
                                          'nova-compute', False)
            time.sleep(2)
            self.check_host_status('up')

    def check_host_status(self, state):
        service = self.nova.services.list(host=self.down_host.name,
                                          binary='nova-compute')
        host_state = service[0].__dict__.get('state')
        assert host_state == state

    def get_disable_network_log(self):
        if self.GetLog:
            self.log.info('Already get the disable_netork.log '
                          'from down_host......')
            return self.disable_network_log
        if self.down_host is not None:
            client = SSHClient(
                self.down_host.ip,
                self.installer.node_user_name,
                key_filename=self.installer.get_ssh_key_from_installer(),
                look_for_keys=True,
                log=self.log)

            self.disable_network_log = \
                '{0}/{1}'.format(self.test_dir,
                                 'disable_network.log')
            client.scp('disable_network.log',
                       self.disable_network_log,
                       method='get')
            self.log.info('Get the disable_netork.log from'
                          'down_host(host_name:%s, host_ip:%s)'
                          % (self.down_host.name, self.down_host.ip))
        self.GetLog = True
        return self.disable_network_log

    def _set_link_down(self, compute_ip):
        file_name = '{0}/{1}'.format(self.test_dir, 'disable_network.sh')
        with open(file_name, 'w') as file:
            file.write(LINK_DOWN_SCRIPT.format(compute_ip=compute_ip))
        client = SSHClient(
            compute_ip,
            self.installer.node_user_name,
            key_filename=self.installer.get_ssh_key_from_installer(),
            look_for_keys=True,
            log=self.log)
        client.scp(file_name, 'disable_network.sh')
        command = 'bash disable_network.sh > disable_network.log 2>&1 &'
        client.ssh(command)

    def check_notification_time(self):
        if self.consumer.notified_time is None \
                or self.monitor.detected_time is None:
            raise Exception('doctor fault management test failed, '
                            'detected_time=%s, notified_time=%s'
                            % (self.monitor.detected_time,
                               self.consumer.notified_time))
        notification_time = \
            self.consumer.notified_time - \
            self.monitor.detected_time

        self.log.info('doctor fault management notification_time=%s'
                      % notification_time)

        if notification_time < 1 and notification_time > 0:
            self.log.info('doctor fault management test successfully')
        else:
            if self.conf.profiler_type:
                self.log.info('run doctor fault management profile.......')
                self.run_profiler()

            raise Exception('doctor fault management test failed, '
                            'notification_time=%s' % notification_time)

        if self.conf.profiler_type:
            self.log.info('run doctor fault management profile.......')
            self.run_profiler()

    def run_profiler(self):

        net_down_log_file = self.get_disable_network_log()
        reg = '(?<=doctor set link down at )\d+.\d+'
        linkdown = float(match_rep_in_file(reg, net_down_log_file).group(0))

        vmdown = self.inspector.vm_down_time
        hostdown = self.inspector.host_down_time
        detected = self.monitor.detected_time
        notified = self.consumer.notified_time

        if None in [vmdown, hostdown, detected, notified]:
            self.log.info('one of the time for profiler is None, return')
            return

        # TODO(yujunz) check the actual delay to verify time sync status
        # expected ~1s delay from $trigger to $linkdown
        relative_start = linkdown
        os.environ['DOCTOR_PROFILER_T00'] = (
            str(int((linkdown - relative_start) * 1000)))
        os.environ['DOCTOR_PROFILER_T01'] = (
            str(int((detected - relative_start) * 1000)))
        os.environ['DOCTOR_PROFILER_T03'] = (
            str(int((vmdown - relative_start) * 1000)))
        os.environ['DOCTOR_PROFILER_T04'] = (
            str(int((hostdown - relative_start) * 1000)))
        os.environ['DOCTOR_PROFILER_T09'] = (
            str(int((notified - relative_start) * 1000)))

        profiler_main(log=self.log)
