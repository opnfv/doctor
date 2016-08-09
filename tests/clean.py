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
import os

import novaclient.client as novaclient


nova_api_version = '2.11'

def enable_compute_host(hostname):
    self.nova = novaclient.Client(self.nova_api_version,
                                  os.environ['OS_USERNAME'],
                                  os.environ['OS_PASSWORD'],
                                  os.environ['OS_TENANT_NAME'],
                                  os.environ['OS_AUTH_URL'],
                                  connection_pool=True)
    opts = {'all_tenants': True, 'host': hostname}
    for server in self.nova.servers.list(detailed=False, search_opts=opts):
        self.nova.servers.reset_state(server, 'active')
    self.nova.services.force_down(hostname, 'nova-compute', False)


def get_args():
    parser = argparse.ArgumentParser(description='Doctor Test Cleaner')
    parser.add_argument('hostname', metavar='HOSTNAME', type=str, nargs='?',
                        help='a hostname to be re-enable')
    return parser.parse_args()


def main():
    args = get_args()
    enable_compute_host(args.hostname)


if __name__ == '__main__':
    main()
