##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
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

import doctor.clients as os_clients
import doctor.logger as doctor_logger
from doctor.monitor.base import Monitor

ICMP_ECHO_MESSAGE = '\x08\x00\xf7\xff\x00\x00\x00\x00'
LOG = doctor_logger.Logger('doctor_monitor').getLogger()


class SampleMonitor(Monitor):

    def __init__(self, conf, inspector):
        super(SampleMonitor, self).__init__(conf)

        self.inspector_url = inspector.get_inspector_url()
        self.nova = os_clients.nova_client(conf, os_clients.get_session(conf))
        self.hosts = self._filter_computer_hosts(self.nova.hosts.list())

    def _filter_computer_hosts(self, hosts):
        compute_hosts = []
        for host in hosts:
            host_dict = host.__dict__
            if host_dict['service'] and host_dict['service'] == 'compute':
                compute_hosts.append(host_dict)
        return compute_hosts

    def start(self):
        listeners = []
        for host in self.hosts:
            host_name = host['name']
            host_ip = socket.gethostbyname(host_name)
            listener = Listener(self.conf, host_name, host_ip, self.inspector_url)
            listener.start()
            listeners.append(listener)

    def stop(self):
        pass


class Listener(Thread):
    interval = 0.1  # second
    timeout = 0.1   # second
    event_type = "compute.host.down"

    def __init__(self, conf, host_name, host_ip, inspector_url):
        super(Listener).__init__(self)
        self.conf = conf
        self.hostname = host_name
        self.ip_addr = host_ip
        self.inspector_url = inspector_url

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                             socket.IPPROTO_ICMP)
        sock.settimeout(self.timeout)
        while True:
            try:
                sock.sendto(ICMP_ECHO_MESSAGE, (self.ip_addr, 0))
                data = sock.recv(4096)
            except socket.timeout:
                print "doctor monitor detected at %s" % time.time()
                self._report_error()
                print "ping timeout, quit monitoring..."
                exit(0)
            time.sleep(self.interval)

    def stop(self):
        pass

    def _report_error(self):
        data = [
            {
                'time': datetime.now().isoformat(),
                'type': self.event_type,
                'details': {
                    'hostname': self.hostname,
                    'status': 'down',
                    'monitor': 'monitor_sample',
                    'monitor_event_id': 'monitor_sample_event1'
                },
            },
        ]

        auth_token = os_clients.get_session(self.conf).get_token() if \
                     self.conf.inspector_type == 'congress' else None
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token,
        }

        requests.put(self.inspector_url, data=json.dumps(data), headers=headers)
