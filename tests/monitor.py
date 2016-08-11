##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import argparse
from datetime import datetime
import json
import os
import requests
import socket
import sys
import time

from congressclient.v1 import client
from keystoneclient import session as ksc_session
from keystoneclient.auth.identity import v2

# NOTE: icmp message with all zero data (checksum = 0xf7ff)
#       see https://tools.ietf.org/html/rfc792
ICMP_ECHO_MESSAGE = '\x08\x00\xf7\xff\x00\x00\x00\x00'

SUPPORTED_INSPECTOR_TYPES = ['sample', 'congress']

class DoctorMonitorSample(object):

    interval = 0.1  # second
    timeout = 0.1  # second
    event_type = "compute.host.down"

    def __init__(self, args):
        if args.inspector_type not in SUPPORTED_INSPECTOR_TYPES:
            raise Exception("Inspector type '%s' not supported", args.inspector_type)

        self.hostname = args.hostname
        self.inspector_url = args.inspector_url
        self.inspector_type = args.inspector_type
        self.ip_addr = args.ip or socket.gethostbyname(self.hostname)

        if self.inspector_type == 'congress':
            auth = v2.Password(auth_url=os.environ['OS_AUTH_URL'],
                               username=os.environ['OS_USERNAME'],
                               password=os.environ['OS_PASSWORD'],
                               tenant_name=os.environ['OS_TENANT_NAME'])
            self.session = ksc_session.Session(auth=auth)

            congress = client.Client(session=self.session, service_type='policy')
            ds = congress.list_datasources()['results']
            doctor_ds = next((item for item in ds if item['driver'] == 'doctor'),
                             None)

            congress_endpoint = congress.httpclient.get_endpoint(auth=auth)
            self.inspector_url = ('%s/v1/data-sources/%s/tables/events/rows' %
                                  (congress_endpoint, doctor_ds['id']))

    def start_loop(self):
        print "start ping to host %(h)s (ip=%(i)s)" % {'h': self.hostname,
                                                       'i': self.ip_addr}
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                             socket.IPPROTO_ICMP)
        sock.settimeout(self.timeout)
        while True:
            try:
                sock.sendto(ICMP_ECHO_MESSAGE, (self.ip_addr, 0))
                data = sock.recv(4096)
            except socket.timeout:
                print "doctor monitor detected at %s" % time.time()
                self.report_error()
                print "ping timeout, quit monitoring..."
                return
            time.sleep(self.interval)

    def report_error(self):
        if self.inspector_type == 'sample':
            payload = {"type": self.event_type, "hostname": self.hostname}
            data = json.dumps(payload)
            headers = {'content-type': 'application/json'}
            requests.post(self.inspector_url, data=data, headers=headers)
        elif self.inspector_type == 'congress':
            data = [
                {
                    'id': 'monitor_sample_id1',
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

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Auth-Token':self.session.get_token(),
            }

            requests.put(self.inspector_url, data=json.dumps(data), headers=headers)


def get_args():
    parser = argparse.ArgumentParser(description='Doctor Sample Monitor')
    parser.add_argument('hostname', metavar='HOSTNAME', type=str, nargs='?',
                        help='a hostname to monitor connectivity')
    parser.add_argument('ip', metavar='IP', type=str, nargs='?',
                        help='an IP address to monitor connectivity')
    parser.add_argument('inspector_type', metavar='INSPECTOR_TYPE', type=str, nargs='?',
                        help='inspector to report',
                        default='sample')
    parser.add_argument('inspector_url', metavar='INSPECTOR_URL', type=str, nargs='?',
                        help='inspector url to report error',
                        default='http://127.0.0.1:12345/events')
    return parser.parse_args()


def main():
    args = get_args()
    monitor = DoctorMonitorSample(args)
    monitor.start_loop()


if __name__ == '__main__':
    main()
