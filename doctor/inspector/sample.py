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
import os

import doctor.clients as os_client
import doctor.logger as doctor_logger
from doctor import nova_force_down
from doctor.inspector.base import Inspector

Log = doctor_logger.Logger("inspector").getLogger()

app = Flask('inspector')


@app.route('/events', methods=['POST'])
def event_posted():
    Log.debug('event posted at %s' % time.time())
    Log.debug('inspector = %s' % inspector)
    Log.debug('received data = %s' % request.data)
    d = json.loads(request.data)
    hostname = d['details']['hostname']
    event_type = d['type']
    if event_type == 'compute.host.down':
        sample_inspector.disable_compute_host(hostname)
    return "OK"

    
class SampleInspector(Inspector):

    global app

    def __init__(self, conf):
        super(SampleInspector, self).__init__(conf)
        self.servers = collections.defaultdict(list)
        self.nova = os_client.nova_client(conf)
        self.inspector_url = self.get_inspector_url()
        self.init_servers_list()

    def get_inspector_url(self):
        return self.conf.inspector.inspector_url

    def init_servers_list(self):
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
        nova_force_down.force_down(hostname)

    def start(self):
        app.run(host="0.0.0.0", port=self.conf.inspector_port)


