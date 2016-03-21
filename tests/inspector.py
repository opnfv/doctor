##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import argparse
from flask import Flask
from flask import request
import json
import os

import novaclient.client as novaclient

import nova_force_down


class DoctorInspectorSample(object):

    nova_api_version = 2.11

    def __init__(self):
        self.nova = novaclient.Client(self.nova_api_version,
                                      os.environ['OS_USERNAME'],
                                      os.environ['OS_PASSWORD'],
                                      os.environ['OS_TENANT_NAME'],
                                      os.environ['OS_AUTH_URL'],
                                      connection_pool=True)
        # check nova is available
        self.nova.servers.list(detailed=False)

    def disable_compute_host(self, hostname):
        opts = {'all_tenants': True, 'host': hostname}
        for server in self.nova.servers.list(detailed=False, search_opts=opts):
            self.nova.servers.reset_state(server, 'error')

        # NOTE: We use our own client here instead of this novaclient for a
        #       workaround.  Once keystone provides v2.1 nova api endpoint
        #       in the service catalog which is configured by OpenStack
        #       installer, we can use this:
        #
        # self.nova.services.force_down(hostname, 'nova-compute', True)
        #
        nova_force_down.force_down(hostname)


app = Flask(__name__)
inspector = DoctorInspectorSample()


@app.route('/events', methods=['POST'])
def event_posted():
    app.logger.debug('event posted')
    app.logger.debug('inspector = %s' % inspector)
    app.logger.debug('received data = %s' % request.data)
    d = json.loads(request.data)
    hostname = d['hostname']
    event_type = d['type']
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
    app.run(port=args.port, debug=True)


if __name__ == '__main__':
    main()
