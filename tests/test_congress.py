##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from datetime import datetime
import json
import os
import requests
import sys

from congressclient.v1 import client
from keystoneclient import session as ksc_session
from keystoneclient.auth.identity import v2


W_ERROR = False

class TestCongress(object):

    def __init__(self):
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
        self.url = ('%s/v1/data-sources/%s/tables/events/rows' %
                    (congress_endpoint, doctor_ds['id']))

    def test_send_to_doctor_driver(self):
        data = [
                {
                    'id': 'id1',
                    'time': datetime.now().isoformat(),
                    'type': 'host.nic1.down',
                    'details': {
                        'hostname': 'compute1',
                        'status': 'down',
                        'monitor': 'monitor1',
                        'monitor_event_id': 'event1'
                    },
                },
        ]

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Auth-Token':self.session.get_token(),
        }

        result = requests.put(self.url, data=json.dumps(data), headers=headers)
        if not (result.status_code == 200):
            global W_ERROR
            W_ERROR = True


def main():
    tc = TestCongress()
    tc.test_send_to_doctor_driver()
    sys.exit(W_ERROR)


if __name__ == '__main__':
    main()
