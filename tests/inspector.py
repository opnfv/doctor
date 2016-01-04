#
# Copyright 2016 NEC Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
from flask import Flask
from flask import request
import json
import os

import novaclient.client as novaclient


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
        self.nova.services.force_down(hostname, 'nova-compute', True)


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
    parser = argparse.ArgumentParser(description='Doctor Sample Monitor')
    parser.add_argument('port', metavar='PORT', type=int, nargs='?',
                        help='a port for inspectpr')
    return parser.parse_args()


def main():
    args = get_args()
    app.run(port=args.port, debug=True)


if __name__ == '__main__':
    main()
