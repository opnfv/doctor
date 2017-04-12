##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from datetime import datetime
import json
import requests
import socket
from threading import Thread
import time

from identity_auth import get_session
from os_clients import nova_client
from monitor.base import BaseMonitor


class SampleMonitor(BaseMonitor):
    event_type = "compute.host.down"

    def __init__(self, conf, inspector_url, log):
        super(SampleMonitor, self).__init__(conf, inspector_url, log)
        self.session = get_session()
        self.nova = nova_client(conf.nova_version, self.session)
        self.hosts = self.nova.hypervisors.list(detailed=True)
        self.pingers = []

    def _filter_computer_hosts(self, hosts):
        compute_hosts = []
        for host in hosts:
            host_dict = host.__dict__
            if 'service' in host_dict and host_dict['service'] == 'compute':
                compute_hosts.append(host_dict)
        return compute_hosts

    def start(self):
        self.log.info('sample monitor start......')
        for host in self.hosts:
            host_dict = host.__dict__
            host_name = host_dict['hypervisor_hostname']
            host_ip = host_dict['host_ip']
            pinger = Pinger(host_name, host_ip, self, self.log)
            pinger.start()
            self.pingers.append(pinger)

    def stop(self):
        self.log.info('sample monitor stop......')
        for pinger in self.pingers:
            pinger.stop()
            pinger.join()
        del self.pingers

    def report_error(self, hostname):
        self.log.info('sample monitor report error......')
        data = [
            {
                'id': 'monitor_sample_id1',
                'time': datetime.now().isoformat(),
                'type': self.event_type,
                'details': {
                    'hostname': hostname,
                    'status': 'down',
                    'monitor': 'monitor_sample',
                    'monitor_event_id': 'monitor_sample_event1'
                },
            },
        ]

        auth_token = self.session.get_token() if \
                     self.conf.inspector.type != 'sample' else None
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token,
        }

        url = '%s%s' % (self.inspector_url, 'events') \
            if self.inspector_url.endswith('/') else \
            '%s%s' % (self.conf.inspector.url, '/events')
        requests.put(url, data=json.dumps(data), headers=headers)


class Pinger(Thread):
    interval = 0.1  # second
    timeout = 0.1   # second
    ICMP_ECHO_MESSAGE = '\x08\x00\xf7\xff\x00\x00\x00\x00'

    def __init__(self, host_name, host_ip, monitor, log):
        Thread.__init__(self)
        self.monitor = monitor
        self.hostname = host_name
        self.ip_addr = host_ip or socket.gethostbyname(self.hostname)
        self.log = log
        self._stopped = False

    def run(self):
        while True:
            if self._stopped:
                return
            self._run()
            time.sleep(self.interval)

    def stop(self):
        self.log.info("Stopping Pinger host_name(%s), host_ip(%s)"
                      % (self.hostname, self.ip_addr))
        self._stopped = True

    def _run(self):
        self.log.info("Starting Pinger host_name(%s), host_ip(%s)"
                      % (self.hostname, self.ip_addr))

        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                             socket.IPPROTO_ICMP)
        sock.settimeout(self.timeout)
        while True:
            try:
                sock.sendto(self.ICMP_ECHO_MESSAGE, (self.ip_addr, 0))
                sock.recv(4096)
            except socket.timeout:
                self.log.info("doctor monitor detected at %s" % time.time())
                self.monitor.report_error(self.hostname)
                self.log.info("ping timeout, quit monitoring...")
                self._stopped = True
