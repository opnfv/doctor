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
import oslo_messaging
import time
from threading import Thread
import requests
import yaml

from doctor_tests.common import utils
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import nova_client
from doctor_tests.os_clients import neutron_client
from doctor_tests.inspector.base import BaseInspector


class SampleInspector(BaseInspector):
    event_type = 'compute.host.down'

    def __init__(self, conf, log, trasport_url):
        super(SampleInspector, self).__init__(conf, log)
        self.inspector_url = self.get_inspector_url()
        self.novaclients = list()
        self._init_novaclients()
        # Normally we use this client for non redundant API calls
        self.nova = self.novaclients[0]

        auth = get_identity_auth(project=self.conf.doctor_project)
        session = get_session(auth=auth)
        if self.conf.inspector.update_neutron_port_dp_status:
            self.neutron = neutron_client(session)

        self.servers = collections.defaultdict(list)
        self.hostnames = list()
        self.app = None

        transport = oslo_messaging.get_notification_transport(self.conf,
                                                              trasport_url)
        self.notif = oslo_messaging.Notifier(transport,
                                             'compute.instance.update',
                                             driver='messaging',
                                             topics=['notifications'])
        self.notif = self.notif.prepare(publisher_id='sample')

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
        servers = self.nova.servers.list(detailed=True, search_opts=opts)
        for server in servers:
            try:
                host = server.__dict__.get('OS-EXT-SRV-ATTR:host')
                self.servers[host].append(server)
                self.log.debug('get hostname=%s from server=%s'
                               % (host, server))
            except Exception as e:
                self.log.info('can not get hostname from server=%s, error=%s'
                              % (server, e))

    def get_inspector_url(self):
        return 'http://%s:%s/events' % (self.conf.inspector.ip,
                                        self.conf.inspector.port)

    def start(self):
        self.log.info('sample inspector start......')
        self._init_servers_list()
        self.app = InspectorApp(self.conf.inspector.port, self, self.log)
        self.app.start()

    def stop(self):
        self.log.info('sample inspector stop......')
        if not self.app:
            return
        for hostname in self.hostnames:
            self.nova.services.force_down(hostname, 'nova-compute', False)

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
                self.hostnames.append(hostname)
                thr0 = self._send_notif(hostname)
                thr1 = self._disable_compute_host(hostname)
                thr2 = self._vms_reset_state('error', hostname)
                if self.conf.inspector.update_neutron_port_dp_status:
                    thr3 = self._set_ports_data_plane_status('DOWN', hostname)
                thr0.join()
                thr1.join()
                thr2.join()
                if self.conf.inspector.update_neutron_port_dp_status:
                    thr3.join()

    def _alarm_data_decoder(self, data):
        if "[" in data or "{" in data:
            # string to list or dict removing unicode
            data = yaml.load(data.replace("u'", "'"))
        return data

    def _alarm_traits_decoder(self, data):
        return ({str(t[0]): self._alarm_data_decoder(str(t[2]))
                for t in data['reason_data']['event']['traits']})

    def maintenance(self, data):
        try:
            payload = self._alarm_traits_decoder(data)
        except:
            payload = ({t[0]: t[2] for t in
                       data['reason_data']['event']['traits']})
            self.log.error('cannot parse alarm data: %s' % payload)
            raise Exception('sample inspector cannot parse alarm.'
                            'Possibly trait data over 256 char')
        self.log.info('sample inspector received data = %s' % payload)

        state = payload['state']
        host = payload['host']

        if state == 'IN_MAINTENANCE':
            self.log.info("sample inspector: disable %s automatic fault "
                          "management" % host)
        elif state == 'MAINTENANCE_COMPLETE':
            self.log.info("sample inspector: enable %s automatic fault "
                          "management" % host)
        else:
            raise("sample inspector couldn't handle state: %s" % state)

    @utils.run_async
    def _disable_compute_host(self, hostname):
        self.nova.services.force_down(hostname, 'nova-compute', True)

        hostdown_time = time.time()
        self.host_down_time = hostdown_time
        self.log.info('doctor mark host(%s) down at %s'
                      % (hostname, hostdown_time))

    @utils.run_async
    def _vms_reset_state(self, state, hostname):

        @utils.run_async
        def _vm_reset_state(nova, server, state):
            nova.servers.reset_state(server, state)
            vmdown_time = time.time()
            self.vm_down_time = vmdown_time
            self.log.info('doctor mark vm(%s) %s at %s'
                          % (server, state, vmdown_time))

        thrs = []
        for nova, server in zip(self.novaclients, self.servers[hostname]):
            t = _vm_reset_state(nova, server, state)
            thrs.append(t)
        for t in thrs:
            t.join()

    @utils.run_async
    def _send_notif(self, hostname):

        @utils.run_async
        def _send_notif(server):
            payload = dict(tenant_id=server.tenant_id,
                           instance_id=server.id,
                           state="error")
            self.notif.info({'some': 'context'}, 'compute.instance.update',
                            payload)
            self.log.info('doctor compute.instance.update vm(%s) error %s'
                          % (server, time.time()))

        thrs = []
        for server in self.servers[hostname]:
            t = _send_notif(server)
            thrs.append(t)
        for t in thrs:
            t.join()

    @utils.run_async
    def _set_ports_data_plane_status(self, status, hostname):
        body = {'data_plane_status': status}

        @utils.run_async
        def _set_port_data_plane_status(port_id):
            self.neutron.update_port(port_id, body)
            self.log.info('doctor set data plane status %s on port %s'
                          % (status, port_id))

        thrs = []
        params = {'binding:host_id': hostname}
        for port_id in self.neutron.list_ports(**params):
            t = _set_port_data_plane_status(port_id)
            thrs.append(t)
        for t in thrs:
            t.join()


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
            self.log.info('event posted in sample inspector at %s'
                          % time.time())
            self.log.info('sample inspector = %s' % self.inspector)
            self.log.info('sample inspector received data = %s'
                          % request.data)
            events = json.loads(request.data.decode('utf8'))
            self.inspector.handle_events(events)
            return "OK"

        @app.route('/maintenance', methods=['POST'])
        def maintenance():
            self.inspector.maintenance(request.json)
            return "OK"

        @app.route('/events/shutdown', methods=['POST'])
        def shutdown():
            self.log.info('shutdown inspector app server at %s' % time.time())
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return 'inspector app shutting down...'

        app.run(host="0.0.0.0", port=self.port)
