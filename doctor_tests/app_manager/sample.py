##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from flask import Flask
from flask import request
import json
import yaml
import time
from threading import Thread
import requests

from doctor_tests.app_manager.base import BaseAppManager
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import nova_client


class SampleAppManager(BaseAppManager):

    def __init__(self, stack, conf, log):
        super(SampleAppManager, self).__init__(conf, log)
        self.stack = stack
        self.app = None

    def start(self):
        self.log.info('sample app manager start......')
        self.app = AppManager(self.stack, self.conf, self, self.log)
        self.app.start()

    def stop(self):
        self.log.info('sample app manager stop......')
        if not self.app:
            return
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        url = 'http://%s:%d/shutdown'\
              % (self.conf.app_manager.ip,
                 self.conf.app_manager.port)
        requests.post(url, data='', headers=headers)


class AppManager(Thread):

    def __init__(self, stack, conf, app_manager, log):
        Thread.__init__(self)
        self.stack = stack
        self.conf = conf
        self.port = self.conf.app_manager.port
        self.app_manager = app_manager
        self.log = log
        self.intance_ids = None
        self.auth = get_identity_auth(project=self.conf.doctor_project)
        self.session = get_session(auth=self.auth)
        self.nova = nova_client(self.conf.nova_version,
                                get_session(auth=self.auth))
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'}
        if self.conf.admin_tool.type == 'fenix':
            self.headers['X-Auth-Token'] = self.session.get_token()
        self.orig_number_of_instances = self.number_of_instances()
        self.ha_instances = self.get_ha_instances()
        self.floating_ip = None
        self.active_instance_id = self.active_instance_id()

    def active_instance_id(self):
        for instance in self.ha_instances:
            network_interfaces = next(iter(instance.addresses.values()))
            for network_interface in network_interfaces:
                _type = network_interface.get('OS-EXT-IPS:type')
                if _type == "floating":
                    if not self.floating_ip:
                        self.floating_ip = network_interface.get('addr')
                    self.log.debug('active_instance: %s %s' %
                                   (instance.name, instance.id))
                    return instance.id
        raise Exception("No active instance found")

    def switch_over_ha_instance(self):
        for instance in self.ha_instances:
            if instance.id != self.active_instance_id:
                self.log.info('Switch over to: %s %s' % (instance.name,
                                                         instance.id))
                instance.add_floating_ip(self.floating_ip)
                self.active_instance_id = instance.id
                break

    def get_instance_ids(self):
        ret = list()
        for instance in self.nova.servers.list(detailed=False):
            ret.append(instance.id)
        return ret

    def get_ha_instances(self):
        ha_instances = list()
        for instance in self.nova.servers.list(detailed=True):
            if "doctor_ha_app_" in instance.name:
                ha_instances.append(instance)
                self.log.debug('ha_instances: %s' % instance.name)
        return ha_instances

    def _alarm_data_decoder(self, data):
        if "[" in data or "{" in data:
            # string to list or dict removing unicode
            data = yaml.load(data.replace("u'", "'"))
        return data

    def _alarm_traits_decoder(self, data):
        return ({str(t[0]): self._alarm_data_decoder(str(t[2]))
                for t in data['reason_data']['event']['traits']})

    def get_session_instance_ids(self, url, session_id):
        ret = requests.get(url, data=None, headers=self.headers)
        if ret.status_code != 200:
            raise Exception(ret.text)
        self.log.info('get_instance_ids %s' % ret.json())
        return ret.json()['instance_ids']

    def scale_instances(self, number_of_instances):
        number_of_instances_before = self.number_of_instances()

        parameters = self.stack.parameters
        parameters['nonha_intances'] += number_of_instances
        self.stack.update(self.stack.stack_name,
                          self.stack.stack_id,
                          self.stack.template,
                          parameters=parameters,
                          files=self.stack.files)

        number_of_instances_after = self.number_of_instances()
        if (number_of_instances_before + number_of_instances !=
           number_of_instances_after):
            self.log.error('scale_instances with: %d from: %d ends up to: %d'
                           % (number_of_instances, number_of_instances_before,
                              number_of_instances_after))
            raise Exception('scale_instances failed')

        self.log.info('scaled insances from %d to %d' %
                      (number_of_instances_before,
                       number_of_instances_after))

    def number_of_instances(self):
        return len(self.nova.servers.list(detailed=False))

    def run(self):
        app = Flask('app_manager')

        @app.route('/maintenance', methods=['POST'])
        def maintenance_alarm():
            data = json.loads(request.data.decode('utf8'))
            try:
                payload = self._alarm_traits_decoder(data)
            except:
                payload = ({t[0]: t[2] for t in
                           data['reason_data']['event']['traits']})
                self.log.error('cannot parse alarm data: %s' % payload)
                raise Exception('sample app manager cannot parse alarm.'
                                'Possibly trait data over 256 char')

            self.log.info('sample app manager received data = %s' % payload)

            state = payload['state']
            reply_state = None
            reply = dict()

            self.log.info('sample app manager state: %s' % state)

            if state == 'MAINTENANCE':
                instance_ids = (self.get_session_instance_ids(
                                payload['instance_ids'],
                                payload['session_id']))
                reply['instance_ids'] = instance_ids
                reply_state = 'ACK_MAINTENANCE'

            elif state == 'SCALE_IN':
                # scale down 2 isntances that is VCPUS equaling to single
                # compute node
                self.scale_instances(-2)
                reply['instance_ids'] = self.get_instance_ids()
                reply_state = 'ACK_SCALE_IN'

            elif state == 'MAINTENANCE_COMPLETE':
                # possibly need to upscale
                number_of_instances = self.number_of_instances()
                if self.orig_number_of_instances > number_of_instances:
                    scale_instances = (self.orig_number_of_instances -
                                       number_of_instances)
                    self.scale_instances(scale_instances)
                reply_state = 'ACK_MAINTENANCE_COMPLETE'

            elif state == 'PREPARE_MAINTENANCE':
                if "MIGRATE" not in payload['allowed_actions']:
                    raise Exception('MIGRATE not supported')

                instance_ids = (self.get_session_instance_ids(
                                payload['instance_ids'],
                                payload['session_id']))
                self.log.info('sample app manager got instances: %s' %
                              instance_ids)
                instance_actions = dict()
                for instance_id in instance_ids:
                    instance_actions[instance_id] = "MIGRATE"
                    if instance_id == self.active_instance_id:
                        self.switch_over_ha_instance()
                reply['instance_actions'] = instance_actions
                reply_state = 'ACK_PREPARE_MAINTENANCE'

            elif state == 'PLANNED_MAINTENANCE':
                if "MIGRATE" not in payload['allowed_actions']:
                    raise Exception('MIGRATE not supported')

                instance_ids = (self.get_session_instance_ids(
                                payload['instance_ids'],
                                payload['session_id']))
                self.log.info('sample app manager got instances: %s' %
                              instance_ids)
                instance_actions = dict()
                for instance_id in instance_ids:
                    instance_actions[instance_id] = "MIGRATE"
                    if instance_id == self.active_instance_id:
                        self.switch_over_ha_instance()
                reply['instance_actions'] = instance_actions
                reply_state = 'ACK_PLANNED_MAINTENANCE'

            elif state == 'INSTANCE_ACTION_DONE':
                self.log.info('%s' % payload['instance_ids'])

            else:
                raise Exception('sample app manager received event with'
                                ' unknown state %s' % state)

            if reply_state:
                reply['session_id'] = payload['session_id']
                reply['state'] = reply_state
                url = payload['reply_url']
                self.log.info('sample app manager reply: %s' % reply)
                requests.put(url, data=json.dumps(reply), headers=self.headers)

            return 'OK'

        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            self.log.info('shutdown app manager server at %s' % time.time())
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return 'app manager shutting down...'

        app.run(host="0.0.0.0", port=self.port)
