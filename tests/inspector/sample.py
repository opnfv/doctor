##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
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
import time
from threading import Thread
import requests

from identity_auth import get_identity_auth
from identity_auth import get_session
from os_clients import nova_client
from inspector.base import BaseInspector


class SampleInspector(BaseInspector):
    event_type = 'compute.host.down'

    def __init__(self, conf, log):
        super(SampleInspector, self).__init__(conf, log)
        self.inspector_url = self.get_inspector_url()
        self.novaclients = list()
        self._init_novaclients()
        # Normally we use this client for non redundant API calls
        self.nova = self.novaclients[0]

        self.servers = collections.defaultdict(list)
        self.app = None

    def _init_novaclients(self):
        self.NUMBER_OF_CLIENTS = self.conf.instance_count
        auth = get_identity_auth(project=self.conf.doctor_project)
        session = get_session(auth=auth)
        for i in range(self.NUMBER_OF_CLIENTS):
            self.novaclients.append(
                nova_client(self.conf.nova_version, session))

    def _init_servers_list(self):
        self.servers.clear()
        opts = {'all_tenants': True}
        servers = self.nova.servers.list(search_opts=opts)
        for server in servers:
            try:
                host = server.__dict__.get('OS-EXT-SRV-ATTR:host')
                self.servers[host].append(server)
                self.log.debug('get hostname=%s from server=%s' % (host, server))
            except Exception as e:
                self.log.info('can not get hostname from server=%s' % server)

    def get_inspector_url(self):
        return 'http://%s:%s' % (self.conf.inspector.ip, self.conf.inspector.port)

    def start(self):
        self.log.info('sample inspector start......')
        self._init_servers_list()
        self.app = InspectorApp(self.conf.inspector.port, self, self.log)
        self.app.start()

    def stop(self):
        self.log.info('sample inspector stop......')
        if not self.app:
            return

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        url = '%s%s' % (self.inspector_url, 'shutdown') \
            if self.inspector_url.endswith('/') else \
            '%s%s' % (self.inspector_url, '/shutdown')
        requests.post(url, data='', headers=headers)

    def handle_events(self, events):
        for event in events:
            hostname = event['details']['hostname']
            event_type = event['type']
            if event_type == self.event_type:
                self.disable_compute_host(hostname)

    def disable_compute_host(self, hostname):
        threads = []
        if len(self.servers[hostname]) > self.NUMBER_OF_CLIENTS:
            # TODO(tojuvone): This could be enhanced in future with dynamic
            # reuse of self.novaclients when all threads in use
            self.log.error('%d servers in %s. Can handle only %d'%(
                           self.servers[hostname], hostname, self.NUMBER_OF_CLIENTS))
        for nova, server in zip(self.novaclients, self.servers[hostname]):
            t = ThreadedResetState(nova, "error", server, self.log)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        self.nova.services.force_down(hostname, 'nova-compute', True)
        self.log.info('doctor mark host(%s) down at %s' % (hostname, time.time()))


class ThreadedResetState(Thread):

    def __init__(self, nova, state, server, log):
        Thread.__init__(self)
        self.nova = nova
        self.state = state
        self.server = server
        self.log = log

    def run(self):
        self.nova.servers.reset_state(self.server, self.state)
        self.log.info('doctor mark vm(%s) error at %s' % (self.server, time.time()))


class InspectorApp(Thread):

    def __init__(self, port, inspector, log):
        Thread.__init__(self)
        self.port = port
        self.inspector = inspector
        self.log = log

    def run(self):
        app = Flask('inspector')

        @app.route('/events', methods=['PUT'])
        def event_posted():
            self.log.info('event posted in sample inspector at %s' % time.time())
            self.log.info('sample inspector = %s' % self.inspector)
            self.log.info('sample inspector received data = %s' % request.data)
            events = json.loads(request.data)
            self.inspector.handle_events(events)
            return "OK"

        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            self.log.info('shutdown inspector app server at %s' % time.time())
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return 'inspector app shutting down...'

        app.run(host="0.0.0.0", port=self.port)
