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

def set_servers_active(hostname):
    nova_client = novaclient.Client(nova_api_version,
                                    os.environ['OS_USERNAME'],
                                    os.environ['OS_PASSWORD'],
                                    os.environ['OS_TENANT_NAME'],
                                    os.environ['OS_AUTH_URL'],
                                    connection_pool=True)
    opts = {'all_tenants': True, 'host': hostname}
    for server in nova_client.servers.list(detailed=False, search_opts=opts):
        nova_client.servers.reset_state(server, 'active')


def get_args():
    parser = argparse.ArgumentParser(description='Doctor Test Cleaner')
    parser.add_argument('hostname', metavar='HOSTNAME', type=str, nargs='?',
                        help='servers on the specified host will be reactivated')
    return parser.parse_args()


def main():
    args = get_args()
    set_servers_active(args.hostname)


if __name__ == '__main__':
    main()
