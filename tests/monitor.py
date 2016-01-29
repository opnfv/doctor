##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import argparse
import json
import requests
import socket
import time


# NOTE: icmp message with all zero data (checksum = 0xf7ff)
#       see https://tools.ietf.org/html/rfc792
ICMP_ECHO_MESSAGE = '\x08\x00\xf7\xff\x00\x00\x00\x00'


class DoctorMonitorSample(object):

    interval = 0.1  # second
    timeout = 0.1  # second
    event_type = "compute.host.down"

    def __init__(self, args):
        self.hostname = args.hostname
        self.inspector = args.inspector
        self.ip_addr = socket.gethostbyname(self.hostname)

    def start_loop(self):
        print "start ping to host %s" % self.hostname
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
        payload = {"type": self.event_type, "hostname": self.hostname}
        data = json.dumps(payload)
        headers = {'content-type': 'application/json'}
        requests.post(self.inspector, data=data, headers=headers)


def get_args():
    parser = argparse.ArgumentParser(description='Doctor Sample Monitor')
    parser.add_argument('hostname', metavar='HOSTNAME', type=str, nargs='?',
                        help='a hostname to monitor connectivity')
    parser.add_argument('inspector', metavar='INSPECTOR', type=str, nargs='?',
                        help='inspector url to report error',
                        default='http://127.0.0.1:12345/events')
    return parser.parse_args()


def main():
    args = get_args()
    monitor = DoctorMonitorSample(args)
    monitor.start_loop()


if __name__ == '__main__':
    main()
