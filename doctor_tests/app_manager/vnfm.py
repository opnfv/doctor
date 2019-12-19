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
import requests
from threading import Thread
import time
import uuid
import yaml

from doctor_tests.app_manager.base import BaseAppManager
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import neutron_client
from doctor_tests.os_clients import nova_client
from doctor_tests.os_clients import keystone_client


class VNFM(BaseAppManager):

    def __init__(self, stack, conf, log):
        super(VNFM, self).__init__(conf, log)
        self.stack = stack
        self.app = None

    def start(self):
        self.log.info('VNFM start......')
        self.app = VNFManager(self.stack, self.conf, self, self.log)
        self.app.start()

    def stop(self):
        self.log.info('VNFM stop......')
        if not self.app:
            return
        self.app.delete_constraints()
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        url = 'http://%s:%d/shutdown'\
              % (self.conf.app_manager.ip,
                 self.conf.app_manager.port)
        requests.post(url, data='', headers=headers)


class VNFManager(Thread):

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
        self.keystone = keystone_client(
            self.conf.keystone_version, self.session)
        self.nova = nova_client(self.conf.nova_version,
                                self.session)
        self.neutron = neutron_client(session=self.session)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'}
        if self.conf.admin_tool.type == 'fenix':
            self.headers['X-Auth-Token'] = self.session.get_token()
        self.orig_number_of_instances = self.number_of_instances()
        # List of instances
        self.ha_instances = []
        self.nonha_instances = []
        # Different instance_id specific constraints {instanse_id: {},...}
        self.instance_constraints = None
        # Update existing instances to instance lists
        self.update_instances()
        nonha_instances = len(self.nonha_instances)
        if nonha_instances < 7:
            self.scale = 2
            self.max_impacted = 2
        else:
            self.scale = int((nonha_instances) / 2)
            self.max_impacted = self.scale - 1
        self.log.info('Init nonha_instances: %s scale: %s: max_impacted %s' %
                      (nonha_instances, self.scale, self.max_impacted))
        # Different instance groups constraints dict
        self.ha_group = None
        self.nonha_group = None
        # Floating IP used in HA instance
        self.floating_ip = None
        # VNF project_id
        self.project_id = None
        # HA instance_id that is active / has floating IP
        self.active_instance_id = self.active_instance_id()

        services = self.keystone.services.list()
        for service in services:
            if service.type == 'maintenance':
                self.log.info('maintenance service: %s:%s type %s'
                              % (service.name, service.id, service.type))
                maint_id = service.id
        self.maint_endpoint = [ep.url for ep in self.keystone.endpoints.list()
                               if ep.service_id == maint_id and
                               ep.interface == 'public'][0]
        self.log.info('maintenance endpoint: %s' % self.maint_endpoint)

        self.update_constraints()

    def delete_remote_instance_constraints(self, instance_id):
        url = "%s/instance/%s" % (self.maint_endpoint, instance_id)
        self.log.info('DELETE: %s' % url)
        ret = requests.delete(url, data=None, headers=self.headers)
        if ret.status_code != 200 and ret.status_code != 204:
            raise Exception(ret.text)

    def update_remote_instance_constraints(self, instance):
        url = "%s/instance/%s" % (self.maint_endpoint, instance["instance_id"])
        self.log.info('PUT: %s' % url)
        ret = requests.put(url, data=json.dumps(instance),
                           headers=self.headers)
        if ret.status_code != 200 and ret.status_code != 204:
            raise Exception(ret.text)

    def delete_remote_group_constraints(self, instance_group):
        url = "%s/instance_group/%s" % (self.maint_endpoint,
                                        instance_group["group_id"])
        self.log.info('DELETE: %s' % url)
        ret = requests.delete(url, data=None, headers=self.headers)
        if ret.status_code != 200 and ret.status_code != 204:
            raise Exception(ret.text)

    def update_remote_group_constraints(self, instance_group):
        url = "%s/instance_group/%s" % (self.maint_endpoint,
                                        instance_group["group_id"])
        self.log.info('PUT: %s' % url)
        ret = requests.put(url, data=json.dumps(instance_group),
                           headers=self.headers)
        if ret.status_code != 200 and ret.status_code != 204:
            raise Exception(ret.text)

    def delete_constraints(self):
        if self.conf.admin_tool.type == 'fenix':
            self.headers['X-Auth-Token'] = self.session.get_token()
        for instance_id in self.instance_constraints:
            self.delete_remote_instance_constraints(instance_id)
        self.delete_remote_group_constraints(self.nonha_group)
        self.delete_remote_group_constraints(self.ha_group)

    def update_constraints(self):
        self.log.info('Update constraints')
        if self.project_id is None:
            self.project_id = self.keystone.projects.list(
                name=self.conf.doctor_project)[0].id
        if self.nonha_group is None:
            # Nova does not support groupping instances that do not belong to
            # anti-affinity server_groups. Anyhow all instances need groupping
            self.nonha_group = {
                "group_id": str(uuid.uuid4()),
                "project_id": self.project_id,
                "group_name": "doctor_nonha_app_group",
                "anti_affinity_group": False,
                "max_instances_per_host": 0,
                "max_impacted_members": self.max_impacted,
                "recovery_time": 2,
                "resource_mitigation": True}
            self.log.info('create doctor_nonha_app_group constraints: %s'
                          % self.nonha_group)
            self.update_remote_group_constraints(self.nonha_group)
        if self.ha_group is None:
            group_id = [sg.id for sg in self.nova.server_groups.list()
                        if sg.name == "doctor_ha_app_group"][0]
            self.ha_group = {
                "group_id": group_id,
                "project_id": self.project_id,
                "group_name": "doctor_ha_app_group",
                "anti_affinity_group": True,
                "max_instances_per_host": 1,
                "max_impacted_members": 1,
                "recovery_time": 4,
                "resource_mitigation": True}
            self.log.info('create doctor_ha_app_group constraints: %s'
                          % self.nonha_group)
            self.update_remote_group_constraints(self.ha_group)
        instance_constraints = {}
        for ha_instance in self.ha_instances:
            instance = {
                "instance_id": ha_instance.id,
                "project_id": self.project_id,
                "group_id": self.ha_group["group_id"],
                "instance_name": ha_instance.name,
                "max_interruption_time": 120,
                "migration_type": "MIGRATION",
                "resource_mitigation": True,
                "lead_time": 40}
            self.log.info('create ha instance constraints: %s'
                          % instance)
            instance_constraints[ha_instance.id] = instance
        for nonha_instance in self.nonha_instances:
            instance = {
                "instance_id": nonha_instance.id,
                "project_id": self.project_id,
                "group_id": self.nonha_group["group_id"],
                "instance_name": nonha_instance.name,
                "max_interruption_time": 120,
                "migration_type": "MIGRATION",
                "resource_mitigation": True,
                "lead_time": 40}
            self.log.info('create nonha instance constraints: %s'
                          % instance)
            instance_constraints[nonha_instance.id] = instance
        if not self.instance_constraints:
            # Initial instance constraints
            self.log.info('create initial instances constraints...')
            for instance in [instance_constraints[i] for i
                             in instance_constraints]:
                self.update_remote_instance_constraints(instance)
            self.instance_constraints = instance_constraints.copy()
        else:
            self.log.info('check instances constraints changes...')
            added = [i for i in instance_constraints.keys()
                     if i not in self.instance_constraints]
            deleted = [i for i in self.instance_constraints.keys()
                       if i not in instance_constraints]
            modified = [i for i in instance_constraints.keys()
                        if (i not in added and i not in deleted and
                            instance_constraints[i] !=
                            self.instance_constraints[i])]
            for instance_id in deleted:
                self.delete_remote_instance_constraints(instance_id)
            updated = added + modified
            for instance in [instance_constraints[i] in i in updated]:
                self.update_remote_instance_constraints(instance)
            if updated or deleted:
                # Some instance constraints have changed
                self.instance_constraints = instance_constraints.copy()

    def active_instance_id(self):
        # Need rertry as it takes time after heat template done before
        # Floating IP in place
        retry = 5
        while retry > 0:
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
            time.sleep(2)
            self.update_instances()
            retry -= 1
        raise Exception("No active instance found")

    def switch_over_ha_instance(self):
        for instance in self.ha_instances:
            if instance.id != self.active_instance_id:
                self.log.info('Switch over to: %s %s' % (instance.name,
                                                         instance.id))
                # Deprecated, need to use neutron instead
                # instance.add_floating_ip(self.floating_ip)
                port = self.neutron.list_ports(device_id=instance.id)['ports'][0]['id']  # noqa
                floating_id = self.neutron.list_floatingips(floating_ip_address=self.floating_ip)['floatingips'][0]['id']  # noqa
                self.neutron.update_floatingip(floating_id, {'floatingip': {'port_id': port}})  # noqa
                # Have to update ha_instances as floating_ip changed
                self.update_instances()
                self.active_instance_id = instance.id
                break

    def get_instance_ids(self):
        ret = list()
        for instance in self.nova.servers.list(detailed=False):
            ret.append(instance.id)
        return ret

    def update_instances(self):
        instances = self.nova.servers.list(detailed=True)
        self.ha_instances = [i for i in instances
                             if "doctor_ha_app_" in i.name]
        self.nonha_instances = [i for i in instances
                                if "doctor_nonha_app_" in i.name]

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

        self.log.info('scaled instances from %d to %d' %
                      (number_of_instances_before,
                       number_of_instances_after))

    def number_of_instances(self):
        return len(self.nova.servers.list(detailed=False))

    def run(self):
        app = Flask('VNFM')

        @app.route('/maintenance', methods=['POST'])
        def maintenance_alarm():
            data = json.loads(request.data.decode('utf8'))
            try:
                payload = self._alarm_traits_decoder(data)
            except Exception:
                payload = ({t[0]: t[2] for t in
                           data['reason_data']['event']['traits']})
                self.log.error('cannot parse alarm data: %s' % payload)
                raise Exception('VNFM cannot parse alarm.'
                                'Possibly trait data over 256 char')

            self.log.info('VNFM received data = %s' % payload)

            state = payload['state']
            reply_state = None
            reply = dict()

            self.log.info('VNFM state: %s' % state)

            if state == 'MAINTENANCE':
                instance_ids = (self.get_session_instance_ids(
                                payload['instance_ids'],
                                payload['session_id']))
                reply['instance_ids'] = instance_ids
                reply_state = 'ACK_MAINTENANCE'

            elif state == 'SCALE_IN':
                # scale down "self.scale" instances that is VCPUS equaling
                # at least a single compute node
                self.scale_instances(-self.scale)
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
                # TBD from contraints
                if "MIGRATE" not in payload['allowed_actions']:
                    raise Exception('MIGRATE not supported')
                instance_ids = payload['instance_ids'][0]
                self.log.info('VNFM got instance: %s' % instance_ids)
                if instance_ids == self.active_instance_id:
                    self.switch_over_ha_instance()
                # optional also in contraints
                reply['instance_action'] = "MIGRATE"
                reply_state = 'ACK_PREPARE_MAINTENANCE'

            elif state == 'PLANNED_MAINTENANCE':
                # TBD from contraints
                if "MIGRATE" not in payload['allowed_actions']:
                    raise Exception('MIGRATE not supported')
                instance_ids = payload['instance_ids'][0]
                self.log.info('VNFM got instance: %s' % instance_ids)
                if instance_ids == self.active_instance_id:
                    self.switch_over_ha_instance()
                # optional also in contraints
                reply['instance_action'] = "MIGRATE"
                reply_state = 'ACK_PLANNED_MAINTENANCE'

            elif state == 'INSTANCE_ACTION_DONE':
                # TBD was action done in allowed window
                self.log.info('%s' % payload['instance_ids'])
            else:
                raise Exception('VNFM received event with'
                                ' unknown state %s' % state)

            if reply_state:
                if self.conf.admin_tool.type == 'fenix':
                    self.headers['X-Auth-Token'] = self.session.get_token()
                reply['session_id'] = payload['session_id']
                reply['state'] = reply_state
                url = payload['reply_url']
                self.log.info('VNFM reply: %s' % reply)
                requests.put(url, data=json.dumps(reply), headers=self.headers)

            return 'OK'

        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            self.log.info('shutdown VNFM server at %s' % time.time())
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return 'VNFM shutting down...'

        app.run(host="0.0.0.0", port=self.port)
