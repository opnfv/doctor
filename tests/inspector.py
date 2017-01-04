##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import argparse
import collections
from flask import Flask
from flask import request
import json
import logger as doctor_log
import os
import threading
import time

import novaclient.client as novaclient

import nova_force_down

LOG = doctor_log.Logger('doctor_inspector').getLogger()


class ThreadedResetState(threading.Thread):

    def __init__(self, nova, state, server):
        threading.Thread.__init__(self)
        self.nova = nova
        self.state = state
        self.server = server
    def run(self):
        self.nova.servers.reset_state(self.server,self.state)
        LOG.info('doctor mark vm(%s) error at %s' % (self.server, time.time()))


class DoctorInspectorSample(object):

    nova_api_version = '2.11'
    number_of_clients = 50

    def __init__(self):
        self.servers = collections.defaultdict(list)
        self.novaclients = list()
        # Pool of novaclients for redundant usage
        for i in range(self.number_of_clients):
            self.novaclients.append(novaclient.Client(self.nova_api_version,
                                    os.environ['OS_USERNAME'],
                                    os.environ['OS_PASSWORD'],
                                    os.environ['OS_TENANT_NAME'],
                                    os.environ['OS_AUTH_URL'],
                                    connection_pool=True))
        # Normally we use this client for non redundant API calls
        self.nova=self.novaclients[0]
        self.nova.servers.list(detailed=False)
        self.init_servers_list()

    def init_servers_list(self):
        opts = {'all_tenants': True}
        servers=self.nova.servers.list(search_opts=opts)
        self.servers.clear()
        for server in servers:
            try:
                host=server.__dict__.get('OS-EXT-SRV-ATTR:host')
                self.servers[host].append(server)
                LOG.debug('get hostname=%s from server=%s' % (host, server))
            except Exception as e:
                LOG.error('can not get hostname from server=%s' % server)

    def disable_compute_host(self, hostname):
        threads = []
        if len(self.servers[hostname]) > self.number_of_clients:
            # TODO(tojuvone): This could be enhanced in future with dynamic
            # reuse of self.novaclients when all threads in use and
            # self.number_of_clients based on amount of cores.
            LOG.error('%d servers in %s. Can handle only %d'%(
                      self.servers[hostname], hostname, self.number_of_clients))
        for nova, server in zip(self.novaclients,self.servers[hostname]):
            t = ThreadedResetState(nova, "error", server)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        # NOTE: We use our own client here instead of this novaclient for a
        #       workaround.  Once keystone provides v2.1 nova api endpoint
        #       in the service catalog which is configured by OpenStack
        #       installer, we can use this:
        #
        # self.nova.services.force_down(hostname, 'nova-compute', True)
        #
        nova_force_down.force_down(hostname)
        LOG.info('doctor mark host(%s) down at %s' % (hostname, time.time()))


app = Flask(__name__)
inspector = DoctorInspectorSample()


@app.route('/events', methods=['POST'])
def event_posted():
    LOG.info('event posted at %s' % time.time())
    LOG.info('inspector = %s' % inspector)
    LOG.info('received data = %s' % request.data)
    d = json.loads(request.data)
    for event in d:
        hostname = event['details']['hostname']
        event_type = event['type']
        if event_type == 'compute.host.down':
            inspector.disable_compute_host(hostname)
    return "OK"


def get_args():
    parser = argparse.ArgumentParser(description='Doctor Sample Inspector')
    parser.add_argument('port', metavar='PORT', type=int, nargs='?',
                        help='a port for inspector')
    return parser.parse_args()


def main():
    args = get_args()
    app.run(port=args.port)


if __name__ == '__main__':
    main()
