##############################################################################
# Copyright (c) 2017 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import collectd
import sys
from datetime import datetime
import json
import requests
import time
from requests.exceptions import ConnectionError

from keystoneauth1 import loading
from keystoneauth1 import session
from congressclient.v1 import client


def write_debug(str_write, write_type, compute_user):
    file_name = ('/home/%s/monitor.log' % compute_user)
    file_tmp = open(file_name, write_type)
    file_tmp.write("%s" % str_write)
    file_tmp.close()


class DoctorMonitorCollectd(object):
    def __init__(self):
        self.control_ip = ''
        self.compute_user = ''
        self.compute_ip = ''
        self.host_name = ''
        self.inspector_type = ''
        self.inspector_url = ''
        self.os_auth_url = ''
        self.os_username = ''
        self.os_password = ''
        self.os_project_name = ''
        self.os_user_domain_name = ''
        self.os_user_domain_id = ''
        self.os_project_domain_name = ''
        self.os_project_domain_id = ''
        self.sess = ''
        self.auth = ''
        self.inspector_notified = 0
        self.start_notifications = 0
        self.monitor_type = 'sample'

    def config_func(self, config):
        for node in config.children:
            key = node.key.lower()
            val = node.values[0]

            if key == 'compute_host':
                self.host_name = val
            elif key == 'control_ip':
                self.control_ip = val
            elif key == 'compute_ip':
                self.compute_ip = val
            elif key == 'compute_user':
                self.compute_user = val
            elif key == 'inspector_type':
                self.inspector_type = val
            elif key == 'os_auth_url':
                self.os_auth_url = val
            elif key == 'os_username':
                self.os_username = val
            elif key == 'os_password':
                self.os_password = val
            elif key == 'os_project_name':
                self.os_project_name = val
            elif key == 'os_user_domain_name':
                self.os_user_domain_name = val
            elif key == 'os_user_domain_id':
                self.os_user_domain_id = val
            elif key == 'os_project_domain_name':
                self.os_project_domain_name = val
            elif key == 'os_project_domain_id':
                self.os_project_domain_id = val
            else:
                collectd.info('Unknown config key "%s"' % key)

    def init_collectd(self):
        write_debug("Compute node collectd monitor start at %s\n\n"
                    % datetime.now().isoformat(), "w", self.compute_user)

        if self.inspector_type == 'sample':
            self.inspector_url = ('http://%s:12345/events' % self.control_ip)
        elif self.inspector_type == 'congress':
            loader = loading.get_plugin_loader('password')
            self.auth = loader.load_from_options(
                auth_url=self.os_auth_url,
                username=self.os_username,
                password=self.os_password,
                project_name=self.os_project_name,
                user_domain_name=self.os_user_domain_name,
                user_domain_id=self.os_user_domain_id,
                project_domain_name=self.os_project_domain_name,
                project_domain_id=self.os_project_domain_id)
            self.sess = session.Session(auth=self.auth)
            congress = client.Client(session=self.sess, service_type='policy')
            ds = congress.list_datasources()['results']
            doctor_ds = next(
                (item for item in ds if item['driver'] == 'doctor'), None)

            congress_endpoint = \
                congress.httpclient.get_endpoint(auth=self.auth)
            self.inspector_url = ('%s/v1/data-sources/%s/tables/events/rows'
                                  % (congress_endpoint, doctor_ds['id']))
        else:
            sys.exit()
        self.start_notifications = 1

    def notify_inspector(self):
        event_type = "compute.host.down"
        payload = [
            {
                'id': ("monitor_%s_id1" % self.monitor_type),
                'time': datetime.now().isoformat(),
                'type': event_type,
                'details': {
                    'hostname': self.host_name,
                    'status': 'down',
                    'monitor': ("monitor_%s" % self.monitor_type),
                    'monitor_event_id':
                        ("monitor_%s_event1" % self.monitor_type)
                },
            },
        ]
        data = json.dumps(payload)
        self.inspector_notified = 1

        if self.inspector_type == 'sample':
            headers = {'content-type': 'application/json'}
            try:
                requests.post(self.inspector_url, data=data, headers=headers)
            except ConnectionError as err:
                print(err)
        elif self.inspector_type == 'congress':
            # TODO(umar) enhance for token expiry case
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Auth-Token': self.sess.get_token()
            }
            requests.put(self.inspector_url, data=data, headers=headers)

    def handle_notify(self, notification, data=None):
        if (notification.seerity == collectd.NOTIF_FAILURE or
                notification.severity == collectd.NOTIF_WARNING):
            if (self.start_notifications == 1 and
                    self.inspector_notified == 0):
                write_debug("Received down notification:"
                            "doctor monitor detected at %s\n"
                            % time.time(), "a", self.compute_user)
                self.notify_inspector()

        elif notification.severity == collectd.NOTIF_OKAY:
            collectd.info("Interface status: UP again %s\n" % time.time())
        else:
            collectd.info("Unknown notification severity %s\n"
                          % notification.severity)


monitor = DoctorMonitorCollectd()

collectd.register_config(monitor.config_func)
collectd.register_init(monitor.init_collectd)
collectd.register_notification(monitor.handle_notify)
