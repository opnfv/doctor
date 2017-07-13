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
from netifaces import interfaces, ifaddresses, AF_INET
from datetime import datetime
import json
import requests
import time
from requests.exceptions import ConnectionError

from keystoneauth1 import loading
from keystoneauth1 import session
from congressclient.v1 import client

control_ip = ''
compute_user = ''
compute_ip = ''
host_name = ''
inspector_type = ''
inspector_url = ''
os_auth_url = ''
os_username = ''
os_password = ''
os_project_name = ''
os_user_domain_name = ''
os_user_domain_id = ''
os_project_domain_name = ''
os_project_domain_id = ''
sess = ''
auth = ''
inspector_notified = 0
start_notifications = 0
monitor_type = 'sample'

def write_debug(str_write, write_type):
    file_name = ('/home/%s/monitor.log' % compute_user)
    file_tmp = open(file_name, write_type)
    file_tmp.write( "%s" % str_write)
    file_tmp.close()


def config_func(config):
    for node in config.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'compute_host':
            global host_name
            host_name = val
        elif key == 'control_ip':
            global control_ip
            control_ip = val
        elif key == 'compute_ip':
            global compute_ip
            compute_ip = val
        elif key == 'compute_user':
            global compute_user
            compute_user = val
        elif key == 'inspector_type':
            global inspector_type
            inspector_type = val
        elif key == 'os_auth_url':
            global os_auth_url
            os_auth_url = val
        elif key == 'os_username':
            global os_username
            os_username = val
        elif key == 'os_password':
            global os_password
            os_password = val
        elif key == 'os_project_name':
            global os_project_name
            os_project_name = val
        elif key == 'os_user_domain_name':
            global os_user_domain_name
            os_user_domain_name = val
        elif key == 'os_user_domain_id':
            global os_user_domain_id
            os_user_domain_id = val
        elif key == 'os_project_domain_name':
            global os_project_domain_name
            os_project_domain_name = val
        elif key == 'os_project_domain_id':
            global os_project_domain_id
            os_project_domain_id = val
        else:
            collectd.info('Unknown config key "%s"' % key)


def notify_inspector():
    event_type = "compute.host.down"
    payload = [
         {
             'id': ("monitor_%s_id1" % monitor_type),
             'time': datetime.now().isoformat(),
             'type': event_type,
             'details': {
                 'hostname': host_name,
                 'status': 'down',
                 'monitor': ("monitor_%s" % monitor_type),
                 'monitor_event_id': ("monitor_%s_event1" % monitor_type)
             },
         },
    ]
    data = json.dumps(payload)
    global inspector_notified
    inspector_notified = 1

    if inspector_type == 'sample':
        headers = {'content-type': 'application/json'}
        try:
            write_debug("inspector_url %s\n data %s\n headers %s\n" % (inspector_url, data, headers), "a")
            requests.post(inspector_url, data=data, headers=headers)
        except ConnectionError as err:
            print err
    elif inspector_type == 'congress':
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Auth-Token':sess.get_token()
        }
        requests.put(inspector_url, data=data, headers=headers)
        collectd.info("url %s data %s headers %s" % (inspector_url, data, headers))


def init_func():
    global inspector_url, compute_ip, inspector_type
    global auth, sess, os_auth_url, os_username, os_password
    global os_project_name, os_user_domain_name, os_user_domain_id
    global os_project_domain_name, os_project_domain_id

    write_debug("Compute node collectd monitor start at %s\n\n" % datetime.now().isoformat(), "w")
    
    if inspector_type == 'sample':
        inspector_url = ('http://%s:12345/events' % control_ip)
    elif inspector_type == 'congress':
        loader = loading.get_plugin_loader('password')
        global auth
        auth = loader.load_from_options(auth_url=os_auth_url,
                    username=os_username,
                    password=os_password,
                    project_name=os_project_name,
                    user_domain_name=os_user_domain_name,
                    user_domain_id=os_user_domain_id,
                    project_domain_name=os_project_domain_name,
                    project_domain_id=os_project_domain_id)
        global sess
        sess=session.Session(auth=auth)
        congress = client.Client(session=sess, service_type='policy')
        ds = congress.list_datasources()['results']
        doctor_ds = next((item for item in ds if item['driver'] == 'doctor'),
                         None)

        congress_endpoint = congress.httpclient.get_endpoint(auth=auth)
        inspector_url = ('%s/v1/data-sources/%s/tables/events/rows' %
                              (congress_endpoint, doctor_ds['id']))
    else:
        sys.exit()
    global start_notifications
    start_notifications = 1


def handle_notif(notification, data=None):
    global inspector_notified
    global start_notifications
    if (notification.severity == collectd.NOTIF_FAILURE or
        notification.severity == collectd.NOTIF_WARNING):
        if (start_notifications == 1 and inspector_notified == 0):
            write_debug("Received down notification: doctor monitor detected at %s\n" % time.time(), "a")
            notify_inspector()

    elif notification.severity == collectd.NOTIF_OKAY:
        collectd.info("Interface status: UP again %s\n" % time.time())
    else:
        collectd.info("Unknown notification severity %s\n" % notification.severity)


collectd.register_config(config_func)
collectd.register_init(init_func)
collectd.register_notification(handle_notif)
