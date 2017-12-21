##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import congress_client

from doctor_tests.inspector.base import BaseInspector


class CongressInspector(BaseInspector):
    nova_api_min_version = '2.11'
    doctor_driver = 'doctor'
    doctor_datasource = 'doctor'
    policy = 'classification'
    rules = {
        'host_down':
            'host_down(host) :- doctor:events(hostname=host, type="compute.host.down", status="down")',       # noqa
        'active_instance_in_host':
            'active_instance_in_host(vmid, host) :- nova:servers(id=vmid, host_name=host, status="ACTIVE")',  # noqa
        'host_force_down':
            'execute[nova:services.force_down(host, "nova-compute", "True")] :- host_down(host)',             # noqa
        'error_vm_states':
            'execute[nova:servers.reset_state(vmid, "error")] :- host_down(host), active_instance_in_host(vmid, host)'    # noqa
    }

    def __init__(self, conf, log):
        super(CongressInspector, self).__init__(conf, log)
        self.auth = get_identity_auth()
        self.congress = congress_client(get_session(auth=self.auth))
        self._init_driver_and_ds()
        self.inspector_url = self.get_inspector_url()

    def _init_driver_and_ds(self):
        datasources = \
            {ds['name']: ds for ds in
             self.congress.list_datasources()['results']}

        # check nova_api version
        nova_api_version = datasources['nova']['config'].get('api_version')
        if nova_api_version and nova_api_version < self.nova_api_min_version:
            raise Exception('Congress Nova datasource API '
                            'version < nova_api_min_version(%s)'
                            % self.nova_api_min_version)

        # create doctor datasource if it's not exist
        if self.doctor_datasource not in datasources:
            self.congress.create_datasource(
                body={'driver': self.doctor_driver,
                      'name': self.doctor_datasource})

        # check whether doctor driver exist
        drivers = \
            {driver['id']: driver for driver in
             self.congress.list_drivers()['results']}
        if self.doctor_driver not in drivers:
            raise Exception('Do not support doctor driver in congress')

        self.policy_rules = \
            {rule['name']: rule for rule in
             self.congress.list_policy_rules(self.policy)['results']}

    def get_inspector_url(self):
        ds = self.congress.list_datasources()['results']
        doctor_ds = next((item for item in ds if item['driver'] == 'doctor'),
                         None)
        congress_endpoint = \
            self.congress.httpclient.get_endpoint(auth=self.auth)
        return ('%s/v1/data-sources/%s/tables/events/rows' %
                (congress_endpoint, doctor_ds['id']))

    def start(self):
        self.log.info('congress inspector start......')

        for rule_name, rule in self.rules.items():
            self._add_rule(rule_name, rule)

    def stop(self):
        self.log.info('congress inspector stop......')

        for rule_name in self.rules.keys():
            self._del_rule(rule_name)

    def _add_rule(self, rule_name, rule):
        if rule_name not in self.policy_rules:
            self.congress.create_policy_rule(self.policy,
                                             body={'name': rule_name,
                                                   'rule': rule})

    def _del_rule(self, rule_name):
        if rule_name in self.policy_rules:
            rule_id = self.policy_rules[rule_name]['id']
            self.congress.delete_policy_rule(self.policy, rule_id)
