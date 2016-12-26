##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import collections
from flask import Flask
from flask import request
import json
import requests

import doctor.clients as os_client
import doctor.logger as doctor_logger
from doctor.inspector.base import Inspector

Log = doctor_logger.Logger("inspector").getLogger()

app = Flask('inspector')


@app.route('/events', methods=['PUT'])
def event_posted():
    Log.debug('event posted at %s' % time.time())
    Log.debug('inspector = %s' % inspector)
    Log.debug('received data = %s' % request.data)
    d = json.loads(request.data)
    for event in d:
        hostname = d['details']['hostname']
        event_type = d['type']
        if event_type == 'compute.host.down':
            sample_inspector.disable_compute_host(hostname)
    return "OK"


class SampleInspector(Inspector):

    global app

    def __init__(self, conf):
        super(SampleInspector, self).__init__(conf)
        self.inspector_url = self.get_inspector_url()
        self.servers = collections.defaultdict(list)
        self.session = os_client.get_session(self.conf)
        self.nova = os_client.nova_client(self.conf, self.session)
        self.keystone = os_client.keystone_client(self.conf, self.session)
        # check nova is available
        self.nova.servers.list(detailed=False)
        self._init_servers_list()

    def get_inspector_url(self):
        return self.conf.inspector.url

    def _init_servers_list(self):
        opts = {'all_tenants': True}
        servers=self.nova.servers.list(search_opts=opts)
        self.servers.clear()
        for server in servers:
            try:
                host=server.__dict__.get('OS-EXT-SRV-ATTR:host')
                self.servers[host].append(server)
                Log.debug('get hostname=%s from server=%s' % (host, server))
            except Exception as e:
                Log.debug('can not get hostname from server=%s' % server)

    def disable_compute_host(self, hostname):
        for server in self.servers[hostname]:
            self.nova.servers.reset_state(server, 'error')

        # NOTE: We use our own client here instead of this novaclient for a
        #       workaround.  Once keystone provides v2.1 nova api endpoint
        #       in the service catalog which is configured by OpenStack
        #       installer, we can use this:
        #
        # self.nova.services.force_down(hostname, 'nova-compute', True)
        #
        self._force_down(hostname)

    def _force_down(self, hostname, force_down=True):
        for service in self.keystone.auth_ref['serviceCatalog']:
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
            'X-Auth-Token': self.keystone.auth_ref['token']['id'],
            'X-OpenStack-Nova-API-Version': '2.11',
        }

        print requests.put(url, data=json.dumps(data), headers=headers)

    def start(self):
        app.run(host="0.0.0.0", port=self.conf.inspector.port)

    def stop(self):
        pass
