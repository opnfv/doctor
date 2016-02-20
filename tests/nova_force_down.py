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

from keystoneclient.v2_0 import client
import requests


def force_down(hostname, force_down=True):
    keystone = client.Client(username=os.environ['OS_USERNAME'],
                             password=os.environ['OS_PASSWORD'],
                             tenant_name=os.environ['OS_TENANT_NAME'],
                             auth_url=os.environ['OS_AUTH_URL'])

    for service in keystone.auth_ref['serviceCatalog']:
        if service['type'] == 'compute':
            base_url = service['endpoints'][0]['internalURL']
            break

    url = '%s/os-services/force-down' % base_url.replace('/v2/', '/v2.1/')
    data = {
        'forced_down': force_down,
        'binary': 'nova-compute',
        'host': hostname,
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Auth-Token': keystone.auth_ref['token']['id'],
        'X-OpenStack-Nova-API-Version': 2.11,
    }

    print requests.put(url, data=json.dumps(data), headers=headers)


def get_args():
    parser = argparse.ArgumentParser(description='Doctor Test Cleaner')
    parser.add_argument('hostname', metavar='HOSTNAME', type=str, nargs='?',
                        help='a nova-compute hostname to force down')
    parser.add_argument('--unset', action='store_true', default=False,
                        help='unset force_down flag')
    return parser.parse_args()


def main():
    args = get_args()
    force_down(args.hostname, not(args.unset))


if __name__ == '__main__':
    main()
