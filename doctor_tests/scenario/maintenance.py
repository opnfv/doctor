##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import datetime
import json
import requests
import time

from doctor_tests.admin_tool import get_admin_tool
from doctor_tests.app_manager import get_app_manager
from doctor_tests.common.utils import get_doctor_test_root_dir
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.inspector import get_inspector
from doctor_tests.os_clients import keystone_client
from doctor_tests.os_clients import neutron_client
from doctor_tests.os_clients import nova_client
from doctor_tests.stack import Stack


class Maintenance(object):

    def __init__(self, trasport_url, conf, log):
        self.conf = conf
        self.log = log
        self.keystone = keystone_client(
            self.conf.keystone_version, get_session())
        self.nova = nova_client(conf.nova_version, get_session())
        auth = get_identity_auth(project=self.conf.doctor_project)
        self.neutron = neutron_client(get_session(auth=auth))
        self.stack = Stack(self.conf, self.log)
        if self.conf.admin_tool.type == 'sample':
            self.admin_tool = get_admin_tool(trasport_url, self.conf, self.log)
            self.endpoint = 'maintenance'
        else:
            self.endpoint = 'v1/maintenance'
        self.app_manager = get_app_manager(self.stack, self.conf, self.log)
        self.inspector = get_inspector(self.conf, self.log, trasport_url)

    def get_external_network(self):
        ext_net = None
        networks = self.neutron.list_networks()['networks']
        for network in networks:
            if network['router:external']:
                ext_net = network['name']
                break
        if ext_net is None:
            raise Exception("external network not defined")
        return ext_net

    def setup_maintenance(self, user):
        # each hypervisor needs to have same amount of vcpus and they
        # need to be free before test
        hvisors = self.nova.hypervisors.list(detailed=True)
        prev_vcpus = 0
        prev_hostname = ''
        self.log.info('checking hypervisors.......')
        for hvisor in hvisors:
            vcpus = hvisor.__getattr__('vcpus')
            vcpus_used = hvisor.__getattr__('vcpus_used')
            hostname = hvisor.__getattr__('hypervisor_hostname')
            if vcpus < 2:
                raise Exception('not enough vcpus (%d) on %s' %
                                (vcpus, hostname))
            if vcpus_used > 0:
                if self.conf.test_case == 'all':
                    # VCPU might not yet be free after fault_management test
                    self.log.info('%d vcpus used on %s, retry...'
                                  % (vcpus_used, hostname))
                    time.sleep(15)
                    hvisor = self.nova.hypervisors.get(hvisor.id)
                    vcpus_used = hvisor.__getattr__('vcpus_used')
                if vcpus_used > 0:
                    raise Exception('%d vcpus used on %s'
                                    % (vcpus_used, hostname))
            if prev_vcpus != 0 and prev_vcpus != vcpus:
                raise Exception('%d vcpus on %s does not match to'
                                '%d on %s'
                                % (vcpus, hostname,
                                   prev_vcpus, prev_hostname))
            prev_vcpus = vcpus
            prev_hostname = hostname

        # maintenance flavor made so that 2 instances take whole node
        flavor_vcpus = int(vcpus / 2)
        compute_nodes = len(hvisors)
        amount_actstdby_instances = 2
        amount_noredundancy_instances = 2 * compute_nodes - 2
        self.log.info('testing %d computes with %d vcpus each'
                      % (compute_nodes, vcpus))
        self.log.info('testing %d actstdby and %d noredundancy instances'
                      % (amount_actstdby_instances,
                         amount_noredundancy_instances))
        max_instances = (amount_actstdby_instances +
                         amount_noredundancy_instances)
        max_cores = compute_nodes * vcpus

        user.update_quota(max_instances, max_cores)

        test_dir = get_doctor_test_root_dir()
        template_file = '{0}/{1}'.format(test_dir, 'maintenance_hot_tpl.yaml')
        files, template = self.stack.get_hot_tpl(template_file)

        ext_net = self.get_external_network()

        parameters = {'ext_net': ext_net,
                      'flavor_vcpus': flavor_vcpus,
                      'maint_image': self.conf.image_name,
                      'nonha_intances': amount_noredundancy_instances,
                      'ha_intances': amount_actstdby_instances}

        self.log.info('creating maintenance stack.......')
        self.log.info('parameters: %s' % parameters)

        self.stack.create('doctor_test_maintenance',
                          template,
                          parameters=parameters,
                          files=files)

        if self.conf.admin_tool.type == 'sample':
            self.admin_tool.start()
        else:
            # TBD Now we expect Fenix is running in self.conf.admin_tool.port
            pass
        self.app_manager.start()
        self.inspector.start()

    def start_maintenance(self):
        self.log.info('start maintenance.......')
        hvisors = self.nova.hypervisors.list(detailed=True)
        maintenance_hosts = list()
        for hvisor in hvisors:
            hostname = hvisor.__getattr__('hypervisor_hostname')
            maintenance_hosts.append(hostname)

        url = ('http://%s:%s/%s' %
               (self.conf.admin_tool.ip,
                self.conf.admin_tool.port,
                self.endpoint))
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'}

        retries = 12
        while retries > 0:
            # let's start maintenance 20sec from now, so projects will have
            # time to ACK to it before that
            maintenance_at = (datetime.datetime.utcnow() +
                              datetime.timedelta(seconds=30)
                              ).strftime('%Y-%m-%d %H:%M:%S')
            data = {'hosts': [],
                    'state': 'MAINTENANCE',
                    'maintenance_at': maintenance_at,
                    'metadata': {'openstack_version': 'Rocky'},
                    'workflow': 'default'}
            try:
                ret = requests.post(url, data=json.dumps(data),
                                    headers=headers)
            except:
                if retries == 0:
                    raise Exception('admin tool did not respond in 120s')
                else:
                    self.log.info('admin tool not ready, retry in 10s')
                retries = retries - 1
                time.sleep(10)
                continue
            break
        if ret.status_code != 200:
            raise Exception(ret.text)
        return ret.json()['session_id']

    def remove_maintenance_session(self, session_id):
        self.log.info('remove maintenance session %s.......' % session_id)
        url = ('http://%s:%s/%s/%s' %
               (self.conf.admin_tool.ip,
                self.conf.admin_tool.port,
                self.endpoint,
                session_id))

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'}

        ret = requests.delete(url, data=None, headers=headers)
        if ret.status_code != 200:
            raise Exception(ret.text)

    def get_maintenance_state(self, session_id):
        url = ('http://%s:%s/%s/%s' %
               (self.conf.admin_tool.ip,
                self.conf.admin_tool.port,
                self.endpoint,
                session_id))

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'}
        ret = requests.get(url, data=None, headers=headers)
        if ret.status_code != 200:
            raise Exception(ret.text)
        return ret.json()['state']

    def wait_maintenance_complete(self, session_id):
        retries = 90
        state = None
        time.sleep(300)
        while (state not in ['MAINTENANCE_DONE', 'MAINTENANCE_FAILED'] and
               retries > 0):
            time.sleep(10)
            state = self.get_maintenance_state(session_id)
            retries = retries - 1
        self.remove_maintenance_session(session_id)
        self.log.info('maintenance %s ended with state %s' %
                      (session_id, state))
        if state == 'MAINTENANCE_FAILED':
            raise Exception('maintenance %s failed' % session_id)
        elif retries == 0:
            raise Exception('maintenance %s not completed within 20min' %
                            session_id)

    def cleanup_maintenance(self):
        if self.conf.admin_tool.type == 'sample':
            self.admin_tool.stop()
        self.app_manager.stop()
        self.inspector.stop()
        self.log.info('stack delete start.......')
        self.stack.delete()
