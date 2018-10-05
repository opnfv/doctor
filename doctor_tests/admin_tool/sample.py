##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import datetime
from flask import Flask
from flask import request
import json
from novaclient.exceptions import BadRequest
import oslo_messaging as messaging
import requests
import time
from threading import Thread
from traceback import format_exc
from uuid import uuid1 as generate_uuid

from doctor_tests.admin_tool.base import BaseAdminTool
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import aodh_client
from doctor_tests.os_clients import nova_client


class SampleAdminTool(BaseAdminTool):

    def __init__(self, trasport_url, conf, log):
        super(SampleAdminTool, self).__init__(conf, log)
        self.trasport_url = trasport_url
        self.app = None

    def start(self):
        self.log.info('sample admin tool start......')
        self.app = AdminTool(self.trasport_url, self.conf, self, self.log)
        self.app.start()

    def stop(self):
        self.log.info('sample admin tool stop......')
        if not self.app:
            return
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        url = 'http://%s:%d/shutdown'\
              % (self.conf.admin_tool.ip,
                 self.conf.admin_tool.port)
        requests.post(url, data='', headers=headers)


class AdminMain(Thread):

    def __init__(self, trasport_url, session_id, data, parent, conf, log):
        Thread.__init__(self)
        self.session_id = session_id
        self.parent = parent
        self.log = log
        self.conf = conf
        self.url = 'http://%s:%s' % (conf.admin_tool.ip, conf.admin_tool.port)
        self.projects_state = dict()  # current state for each project
        self.proj_server_actions = dict()  # actions for each project server
        self.projects_servers = dict()  # servers processed in current state
        self.maint_proj_servers = dict()  # servers under whole maintenance
        self.hosts = data['hosts']
        self.maintenance_at = data['maintenance_at']
        self.computes_disabled = list()
        self.metadata = data['metadata']
        self.auth = get_identity_auth(project=self.conf.doctor_project)
        self.state = data['state']
        self.aodh = aodh_client(self.conf.aodh_version,
                                get_session(auth=self.auth))
        self.nova = nova_client(self.conf.nova_version,
                                get_session(auth=self.auth))
        self.log.info('transport_url %s' % trasport_url)
        transport = messaging.get_transport(self.conf, trasport_url)
        self.notif_proj = messaging.Notifier(transport,
                                             'maintenance.planned',
                                             driver='messaging',
                                             topics=['notifications'])
        self.notif_proj = self.notif_proj.prepare(publisher_id='admin_tool')
        self.notif_admin = messaging.Notifier(transport,
                                              'maintenance.host',
                                              driver='messaging',
                                              topics=['notifications'])
        self.notif_admin = self.notif_admin.prepare(publisher_id='admin_tool')
        self.stopped = False
        self.log.info('Admin tool session %s initialized' % self.session_id)

    def cleanup(self):
        for host in self.computes_disabled:
            self.log.info('enable nova-compute on %s' % host)
            self.nova.services.enable(host, 'nova-compute')

    def _projects_not_in_wanted_states(self, wanted_states):
        if len([v for v in self.projects_state.values()
               if v not in wanted_states]):
            return True
        else:
            return False

    def projects_not_in_state(self, state):
        if len([v for v in self.projects_state.values()
               if v != state]):
            return True
        else:
            return False

    def wait_projects_state(self, wanted_states, wait_seconds):
        retries = wait_seconds
        while (retries > 0 and
               self._projects_not_in_wanted_states(wanted_states)):
            time.sleep(1)
            retries = retries - 1
        if self._projects_not_in_wanted_states(wanted_states):
            self.log.error('Admin tool session %s: projects in invalid states '
                           '%s' % (self.session_id, self.projects_state))
            return False
        else:
            self.log.info('all projects replied')
            return True

    def _project_notify(self, project_id, instance_ids, allowed_actions,
                        actions_at, state, metadata):
        reply_url = '%s/maintenance/%s/%s' % (self.url, self.session_id,
                                              project_id)

        payload = dict(project_id=project_id,
                       instance_ids=instance_ids,
                       allowed_actions=allowed_actions,
                       state=state,
                       actions_at=actions_at,
                       session_id=self.session_id,
                       metadata=metadata,
                       reply_url=reply_url)

        self.log.debug('Sending "maintenance.planned" to project: %s' %
                       payload)

        self.notif_proj.info({'some': 'context'}, 'maintenance.scheduled',
                             payload)

    def _admin_notify(self, project, host, state, session_id):
        payload = dict(project_id=project, host=host, state=state,
                       session_id=session_id)

        self.log.debug('Sending "maintenance.host": %s' % payload)

        self.notif_admin.info({'some': 'context'}, 'maintenance.host', payload)

    def in_scale(self):
        for project in self.projects_servers:
            self.log.info('SCALE_IN to project %s' % project)
            self.log.debug('instance_ids %s' % self.projects_servers[project])
            instance_ids = '%s/maintenance/%s/%s' % (self.url, self.session_id,
                                                     project)
            allowed_actions = []
            wait_seconds = 120
            actions_at = (datetime.datetime.utcnow() +
                          datetime.timedelta(seconds=wait_seconds)
                          ).strftime('%Y-%m-%d %H:%M:%S')
            state = self.state
            metadata = self.metadata
            self._project_notify(project, instance_ids,
                                 allowed_actions, actions_at, state,
                                 metadata)
        allowed_states = ['ACK_SCALE_IN', 'NACK_SCALE_IN']
        if not self.wait_projects_state(allowed_states, wait_seconds):
            self.state = 'MAINTENANCE_FAILED'
        if self.projects_not_in_state('ACK_SCALE_IN'):
            self.log.error('%s: all states not ACK_SCALE_IN' %
                           self.session_id)
            self.state = 'MAINTENANCE_FAILED'

    def maintenance(self):
        for project in self.projects_servers:
            self.log.info('\nMAINTENANCE to project %s\n' % project)
            self.log.debug('instance_ids %s' % self.projects_servers[project])
            instance_ids = '%s/maintenance/%s/%s' % (self.url, self.session_id,
                                                     project)
            allowed_actions = []
            actions_at = self.maintenance_at
            state = self.state
            metadata = self.metadata
            maint_at = self.str_to_datetime(self.maintenance_at)
            td = maint_at - datetime.datetime.utcnow()
            wait_seconds = int(td.total_seconds())
            if wait_seconds < 10:
                raise Exception('Admin tool session %s: No time for project to'
                                ' answer: %s' %
                                (self.session_id, wait_seconds))
            self._project_notify(project, instance_ids,
                                 allowed_actions, actions_at, state,
                                 metadata)
        allowed_states = ['ACK_MAINTENANCE', 'NACK_MAINTENANCE']
        if not self.wait_projects_state(allowed_states, wait_seconds):
            self.state = 'MAINTENANCE_FAILED'
        if self.projects_not_in_state('ACK_MAINTENANCE'):
            self.log.error('%s: all states not ACK_MAINTENANCE' %
                           self.session_id)
            self.state = 'MAINTENANCE_FAILED'

    def maintenance_complete(self):
        for project in self.projects_servers:
            self.log.info('MAINTENANCE_COMPLETE to project %s' % project)
            instance_ids = '%s/maintenance/%s/%s' % (self.url, self.session_id,
                                                     project)
            allowed_actions = []
            wait_seconds = 120
            actions_at = (datetime.datetime.utcnow() +
                          datetime.timedelta(seconds=wait_seconds)
                          ).strftime('%Y-%m-%d %H:%M:%S')
            state = 'MAINTENANCE_COMPLETE'
            metadata = self.metadata
            self._project_notify(project, instance_ids,
                                 allowed_actions, actions_at, state,
                                 metadata)
        allowed_states = ['ACK_MAINTENANCE_COMPLETE',
                          'NACK_MAINTENANCE_COMPLETE']
        if not self.wait_projects_state(allowed_states, wait_seconds):
            self.state = 'MAINTENANCE_FAILED'
        if self.projects_not_in_state('ACK_MAINTENANCE_COMPLETE'):
            self.log.error('%s: all states not ACK_MAINTENANCE_COMPLETE' %
                           self.session_id)
            self.state = 'MAINTENANCE_FAILED'

    def need_in_scale(self, host_servers):
        room_for_instances = 0
        for host in host_servers:
            instances = 0
            for project in host_servers[host]:
                for instance in host_servers[host][project]:
                    instances += 1
            room_for_instances += (2 - instances)
        self.log.info('there is room for %d instances' % room_for_instances)
        if room_for_instances > 1:
            return False
        else:
            return True

    def find_host_to_be_empty(self, host_servers):
        host_to_be_empty = None
        host_nonha_instances = 0
        for host in host_servers:
            ha_instances = 0
            nonha_instances = 0
            for project in host_servers[host]:
                for instance in host_servers[host][project]:
                    if ('doctor_ha_app_' in
                            host_servers[host][project][instance]):
                        ha_instances += 1
                    else:
                        nonha_instances += 1
            self.log.info('host %s has %d ha and %d non ha instances' %
                          (host, ha_instances, nonha_instances))
            if ha_instances == 0:
                if host_to_be_empty:
                    if nonha_instances < host_nonha_instances:
                        host_to_be_empty = host
                        host_nonha_instances = nonha_instances
                else:
                    host_to_be_empty = host
                    host_nonha_instances = nonha_instances
        self.log.info('host %s selected to be empty' % host_to_be_empty)
        return host_to_be_empty

    def make_compute_host_empty(self, host, projects_servers, statebase):
        state = statebase
        state_ack = 'ACK_%s' % statebase
        state_nack = 'NACK_%s' % statebase
        for project in projects_servers:
            # self.projects_servers must have servers under action
            self.projects_servers[project] = projects_servers[project].copy()
            self.log.info('%s to project %s' % (state, project))
            self.project_servers_log_info(project, projects_servers)
            instance_ids = '%s/maintenance/%s/%s' % (self.url, self.session_id,
                                                     project)
            allowed_actions = ['MIGRATE', 'LIVE_MIGRATE', 'OWN_ACTION']
            wait_seconds = 120
            actions_at = (datetime.datetime.utcnow() +
                          datetime.timedelta(seconds=wait_seconds)
                          ).strftime('%Y-%m-%d %H:%M:%S')
            metadata = self.metadata
            self._project_notify(project, instance_ids,
                                 allowed_actions, actions_at, state,
                                 metadata)
        allowed_states = [state_ack, state_nack]
        if not self.wait_projects_state(allowed_states, wait_seconds):
            self.state = 'MAINTENANCE_FAILED'
        elif self.projects_not_in_state(state_ack):
            self.log.error('%s: all states not %s' %
                           (self.session_id, state_ack))
            self.state = 'MAINTENANCE_FAILED'
        else:
            self.actions_to_have_empty_host(host)

    def notify_action_done(self, project, instance_id):
        instance_ids = instance_id
        allowed_actions = []
        actions_at = None
        state = "INSTANCE_ACTION_DONE"
        metadata = None
        self._project_notify(project, instance_ids, allowed_actions,
                             actions_at, state, metadata)

    def actions_to_have_empty_host(self, host):
        retry = 0
        while len(self.proj_server_actions) == 0:
            time.sleep(2)
            if retry == 10:
                raise Exception('Admin tool session %s: project server actions'
                                ' not set' % self.session_id)
            retry += 1
        for project in self.proj_server_actions:
            for server, action in self.proj_server_actions[project].items():
                self.log.info('Action %s server %s: %s' % (action, server,
                              self.projects_servers[project][server]))
                if action == 'MIGRATE':
                    self.migrate_server(server)
                    self.notify_action_done(project, server)
                elif action == 'OWN_ACTION':
                    pass
                else:
                    raise Exception('Admin tool session %s: server %s action '
                                    '%s not supported' %
                                    (self.session_id, server, action))
        self.proj_server_actions = dict()
        self._wait_host_empty(host)

    def migrate_server(self, server_id):
        server = self.nova.servers.get(server_id)
        vm_state = server.__dict__.get('OS-EXT-STS:vm_state')
        self.log.info('server %s state %s' % (server_id, vm_state))
        last_vm_state = vm_state
        retry_migrate = 5
        while True:
            try:
                server.migrate()
                time.sleep(5)
                retries = 36
                while vm_state != 'resized' and retries > 0:
                    # try to confirm within 3min
                    server = self.nova.servers.get(server_id)
                    vm_state = server.__dict__.get('OS-EXT-STS:vm_state')
                    if vm_state == 'resized':
                        server.confirm_resize()
                        self.log.info('server %s migration confirmed' %
                                      server_id)
                        return
                    if last_vm_state != vm_state:
                        self.log.info('server %s state: %s' % (server_id,
                                      vm_state))
                    if vm_state == 'error':
                        raise Exception('server %s migration failed, state: %s'
                                        % (server_id, vm_state))
                    time.sleep(5)
                    retries = retries - 1
                    last_vm_state = vm_state
                # Timout waiting state to change
                break

            except BadRequest:
                if retry_migrate == 0:
                    raise Exception('server %s migrate failed' % server_id)
                # Might take time for scheduler to sync inconsistent instance
                # list for host
                retry_time = 180 - (retry_migrate * 30)
                self.log.info('server %s migrate failed, retry in %s sec'
                              % (server_id, retry_time))
                time.sleep(retry_time)
            except Exception as e:
                self.log.error('server %s migration failed, Exception=%s' %
                               (server_id, e))
                self.log.error(format_exc())
                raise Exception('server %s migration failed, state: %s' %
                                (server_id, vm_state))
            finally:
                retry_migrate = retry_migrate - 1
        raise Exception('server %s migration timeout, state: %s' %
                        (server_id, vm_state))

    def _wait_host_empty(self, host):
        hid = self.nova.hypervisors.search(host)[0].id
        vcpus_used_last = 0
        # wait 4min to get host empty
        for j in range(48):
            hvisor = self.nova.hypervisors.get(hid)
            vcpus_used = hvisor.__getattr__('vcpus_used')
            if vcpus_used > 0:
                if vcpus_used_last == 0:
                    self.log.info('%s still has %d vcpus reserved. wait...'
                                  % (host, vcpus_used))
                elif vcpus_used != vcpus_used_last:
                    self.log.info('%s still has %d vcpus reserved. wait...'
                                  % (host, vcpus_used))
                vcpus_used_last = vcpus_used
                time.sleep(5)
            else:
                self.log.info('%s empty' % host)
                return
        raise Exception('%s host not empty' % host)

    def projects_listen_alarm(self, match_event):
        match_projects = ([str(alarm['project_id']) for alarm in
                          self.aodh.alarm.list() if
                          str(alarm['event_rule']['event_type']) ==
                          match_event])
        all_projects_match = True
        for project in list(self.projects_state):
            if project not in match_projects:
                self.log.error('Admin tool session %s: project %s not '
                               'listening to %s' %
                               (self.session_id, project, match_event))
                all_projects_match = False
        return all_projects_match

    def project_servers_log_info(self, project, host_servers):
        info = 'Project servers:\n'
        for server in host_servers[project]:
            info += ('  %s: %s\n' %
                     (server, host_servers[project][server]))
        self.log.info('%s' % info)

    def servers_log_info(self, host_servers):
        info = '\n'
        for host in self.hosts:
            info += '%s:\n' % host
            if host in host_servers:
                for project in host_servers[host]:
                    info += '  %s:\n' % project
                    for server in host_servers[host][project]:
                        info += ('    %s: %s\n' %
                                 (server, host_servers[host][project][server]))
        self.log.info('%s' % info)

    def update_server_info(self):
        opts = {'all_tenants': True}
        servers = self.nova.servers.list(search_opts=opts)
        self.projects_servers = dict()
        host_servers = dict()
        for server in servers:
            try:
                host = str(server.__dict__.get('OS-EXT-SRV-ATTR:host'))
                project = str(server.tenant_id)
                server_name = str(server.name)
                server_id = str(server.id)
            except Exception:
                raise Exception('can not get params from server=%s' %
                                server)
            if host not in self.hosts:
                continue
            if host not in host_servers:
                host_servers[host] = dict()
            if project not in host_servers[host]:
                host_servers[host][project] = dict()
            if project not in self.projects_servers:
                self.projects_servers[project] = dict()
            if project not in self.projects_state:
                self.projects_state[project] = None
            host_servers[host][project][server_id] = server_name
            self.projects_servers[project][server_id] = server_name
        return host_servers

    def str_to_datetime(self, dt_str):
        mdate, mtime = dt_str.split()
        year, month, day = map(int, mdate.split('-'))
        hours, minutes, seconds = map(int, mtime.split(':'))
        return datetime.datetime(year, month, day, hours, minutes, seconds)

    def host_maintenance(self, host):
        self.log.info('maintaining host %s' % host)
        # no implementation to make real maintenance
        time.sleep(5)

    def run(self):
        while (self.state not in ['MAINTENANCE_DONE', 'MAINTENANCE_FAILED'] and
               not self.stopped):
            self.log.info('--==session %s: processing state %s==--' %
                          (self.session_id, self.state))
            if self.state == 'MAINTENANCE':
                host_servers = self.update_server_info()
                self.servers_log_info(host_servers)

                if not self.projects_listen_alarm('maintenance.scheduled'):
                    raise Exception('all projects do not listen maintenance '
                                    'alarm')
                self.maintenance()
                if self.state == 'MAINTENANCE_FAILED':
                    continue
                maint_at = self.str_to_datetime(self.maintenance_at)
                if maint_at > datetime.datetime.utcnow():
                    time_now = (datetime.datetime.utcnow().strftime(
                                '%Y-%m-%d %H:%M:%S'))
                    self.log.info('Time now: %s maintenance starts: %s....' %
                                  (time_now, self.maintenance_at))
                    td = maint_at - datetime.datetime.utcnow()
                    time.sleep(td.total_seconds())
                time_now = (datetime.datetime.utcnow().strftime(
                            '%Y-%m-%d %H:%M:%S'))
                self.log.info('Time to start maintenance starts: %s' %
                              time_now)

                # check if we have empty compute host
                # True -> PLANNED_MAINTENANCE
                # False -> check if we can migrate VMs to get empty host
                # True -> PREPARE_MAINTENANCE
                # False -> SCALE_IN
                maintenance_empty_hosts = ([h for h in self.hosts if h not in
                                           host_servers])

                if len(maintenance_empty_hosts) == 0:
                    if self.need_in_scale(host_servers):
                        self.log.info('Need to down scale')
                        self.state = 'SCALE_IN'
                    else:
                        self.log.info('Free capacity, but need empty host')
                        self.state = 'PREPARE_MAINTENANCE'
                else:
                    self.log.info('Free capacity, but need empty host')
                    self.state = 'PLANNED_MAINTENANCE'
                self.log.info('--==State change from MAINTENANCE to %s==--'
                              % self.state)
            elif self.state == 'SCALE_IN':
                # Test case is hard coded to have all compute capacity used
                # We need to down scale to have one empty compute host
                self.update_server_info()
                self.in_scale()
                if self.state == 'MAINTENANCE_FAILED':
                    continue
                self.state = 'PREPARE_MAINTENANCE'
                host_servers = self.update_server_info()
                self.servers_log_info(host_servers)
                self.log.info('--==State change from SCALE_IN to'
                              ' %s==--' % self.state)

            elif self.state == 'PREPARE_MAINTENANCE':
                # It might be down scale did not free capacity on a single
                # compute host, so we need to arrange free capacity to a single
                # compute host
                self.maint_proj_servers = self.projects_servers.copy()
                maintenance_empty_hosts = ([h for h in self.hosts if h not in
                                           host_servers])
                if len(maintenance_empty_hosts) == 0:
                    self.log.info('no empty hosts for maintenance')
                    if self.need_in_scale(host_servers):
                        raise Exception('Admin tool session %s: Not enough '
                                        'free capacity for maintenance' %
                                        self.session_id)
                    host = self.find_host_to_be_empty(host_servers)
                    if host:
                        self.make_compute_host_empty(host, host_servers[host],
                                                     'PREPARE_MAINTENANCE')
                        if self.state == 'MAINTENANCE_FAILED':
                            continue
                    else:
                        # We do not currently support another down scale if
                        # first was not enough
                        raise Exception('Admin tool session %s: No host '
                                        'candidate to be emptied' %
                                        self.session_id)
                else:
                    for host in maintenance_empty_hosts:
                        self.log.info('%s already empty '
                                      'for maintenance' % host)
                self.state = 'PLANNED_MAINTENANCE'
                host_servers = self.update_server_info()
                self.servers_log_info(host_servers)
                self.log.info('--==State change from PREPARE_MAINTENANCE to %s'
                              '==--' % self.state)
            elif self.state == 'PLANNED_MAINTENANCE':
                maintenance_hosts = list()
                maintenance_empty_hosts = list()
                # TODO This should be admin. hack for now to have it work
                admin_project = list(self.projects_state)[0]
                for host in self.hosts:
                    self.log.info('disable nova-compute on host %s' % host)
                    self.nova.services.disable_log_reason(host, 'nova-compute',
                                                          'maintenance')
                    self.computes_disabled.append(host)
                    if host in host_servers and len(host_servers[host]):
                        maintenance_hosts.append(host)
                    else:
                        maintenance_empty_hosts.append(host)
                self.log.info('--==Start to maintain empty hosts==--\n%s' %
                              maintenance_empty_hosts)
                self.update_server_info()
                for host in maintenance_empty_hosts:
                    # scheduler has problems, let's see if just down scaled
                    # host is really empty
                    self._wait_host_empty(host)
                    self.log.info('IN_MAINTENANCE host %s' % host)
                    self._admin_notify(admin_project, host, 'IN_MAINTENANCE',
                                       self.session_id)
                    self.host_maintenance(host)
                    self._admin_notify(admin_project, host,
                                       'MAINTENANCE_COMPLETE',
                                       self.session_id)
                    self.nova.services.enable(host, 'nova-compute')
                    self.computes_disabled.remove(host)
                    self.log.info('MAINTENANCE_COMPLETE host %s' % host)
                self.log.info('--==Start to maintain occupied hosts==--\n%s' %
                              maintenance_hosts)
                for host in maintenance_hosts:
                    self.log.info('PLANNED_MAINTENANCE host %s' % host)
                    self.make_compute_host_empty(host, host_servers[host],
                                                 'PLANNED_MAINTENANCE')
                    if self.state == 'MAINTENANCE_FAILED':
                        continue
                    self.log.info('IN_MAINTENANCE  host %s' % host)
                    self._admin_notify(admin_project, host, 'IN_MAINTENANCE',
                                       self.session_id)
                    self.host_maintenance(host)
                    self._admin_notify(admin_project, host,
                                       'MAINTENANCE_COMPLETE',
                                       self.session_id)
                    self.nova.services.enable(host, 'nova-compute')
                    self.computes_disabled.remove(host)
                    self.log.info('MAINTENANCE_COMPLETE host %s' % host)
                self.state = 'PLANNED_MAINTENANCE_COMPLETE'
                host_servers = self.update_server_info()
                self.servers_log_info(host_servers)
            elif self.state == 'PLANNED_MAINTENANCE_COMPLETE':
                self.log.info('Projects still need to up scale back to full '
                              'capcity')
                self.maintenance_complete()
                if self.state == 'MAINTENANCE_FAILED':
                    continue
                host_servers = self.update_server_info()
                self.servers_log_info(host_servers)
                self.state = 'MAINTENANCE_DONE'
            else:
                raise Exception('Admin tool session %s: session in invalid '
                                'state %s' % (self.session_id, self.state))
        self.log.info('--==Maintenance session %s: %s==--' %
                      (self.session_id, self.state))

    def project_input(self, project_id, data):
        self.log.debug('Admin tool session %s: project %s input' %
                       (self.session_id, project_id))
        if 'instance_actions' in data:
            self.proj_server_actions[project_id] = (
                data['instance_actions'].copy())
        self.projects_state[project_id] = data['state']

    def project_get_instances(self, project_id):
        ret = list(self.projects_servers[project_id])
        self.log.debug('Admin tool session %s: project %s GET return: %s' %
                       (self.session_id, project_id, ret))
        return ret

    def stop(self):
        self.stopped = True


class AdminTool(Thread):

    def __init__(self, trasport_url, conf, admin_tool, log):
        Thread.__init__(self)
        self.admin_tool = admin_tool
        self.log = log
        self.conf = conf
        self.maint_sessions = {}
        self.projects = {}
        self.maintenance_hosts = []
        self.trasport_url = trasport_url

    def run(self):
        app = Flask('admin_tool')

        @app.route('/maintenance', methods=['POST'])
        def admin_maintenance_api_post():
            data = json.loads(request.data.decode('utf8'))
            self.log.info('maintenance message: %s' % data)
            session_id = str(generate_uuid())
            self.log.info('creating session: %s' % session_id)
            self.maint_sessions[session_id] = (
                AdminMain(self.trasport_url,
                          session_id,
                          data,
                          self,
                          self.conf,
                          self.log))
            self.maint_sessions[session_id].start()
            reply = json.dumps({'session_id': session_id,
                                'state': 'ACK_%s' % data['state']})
            self.log.debug('reply: %s' % reply)
            return reply, 200, None

        @app.route('/maintenance/<session_id>', methods=['GET'])
        def admin_maintenance_api_get(session_id=None):
            self.log.debug('Admin get maintenance')
            reply = json.dumps({'state':
                               self.maint_sessions[session_id].state})
            self.log.info('reply: %s' % reply)
            return reply, 200, None

        @app.route('/maintenance/<session_id>/<projet_id>', methods=['PUT'])
        def project_maintenance_api_put(session_id=None, projet_id=None):
            data = json.loads(request.data.decode('utf8'))
            self.log.debug('%s project put: %s' % (projet_id, data))
            self.project_input(session_id, projet_id, data)
            return 'OK'

        @app.route('/maintenance/<session_id>/<projet_id>', methods=['GET'])
        def project_maintenance_api_get(session_id=None, projet_id=None):
            self.log.debug('%s project get %s' % (projet_id, session_id))
            instances = self.project_get_instances(session_id, projet_id)
            reply = json.dumps({'instance_ids': instances})
            self.log.debug('%s reply: %s' % (projet_id, reply))
            return reply, 200, None

        @app.route('/maintenance/<session_id>', methods=['DELETE'])
        def remove_session(session_id=None):
            self.log.info('remove session %s'
                          % session_id)
            self.maint_sessions[session_id].cleanup()
            self.maint_sessions[session_id].stop()
            del self.maint_sessions[session_id]
            return 'OK'

        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            self.log.info('shutdown admin_tool server at %s' % time.time())
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return 'admin_tool app shutting down...'

        app.run(host=self.conf.admin_tool.ip, port=self.conf.admin_tool.port)

    def project_input(self, session_id, project_id, data):
        self.maint_sessions[session_id].project_input(project_id, data)

    def project_get_instances(self, session_id, project_id):
        return self.maint_sessions[session_id].project_get_instances(
            project_id)
