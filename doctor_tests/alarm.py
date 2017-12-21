##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from oslo_config import cfg

from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import aodh_client
from doctor_tests.os_clients import nova_client

OPTS = [
    cfg.StrOpt('alarm_basename',
               default='doctor_alarm',
               help='the base name of alarm',
               required=True),
]


class Alarm(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self.auth = get_identity_auth(project=self.conf.doctor_project)
        self.aodh = \
            aodh_client(conf.aodh_version,
                        get_session(auth=self.auth))
        self.nova = \
            nova_client(conf.nova_version,
                        get_session(auth=self.auth))
        self._init_alarm_name()

    def _init_alarm_name(self):
        self.alarm_names = []
        for i in range(0, self.conf.instance_count):
            alarm_name = '%s%d' % (self.conf.alarm_basename, i)
            self.alarm_names.append(alarm_name)

    def create(self):
        self.log.info('alarm create start......')

        alarms = {alarm['name']: alarm for alarm in self.aodh.alarm.list()}
        servers = \
            {getattr(server, 'name'): server
             for server in self.nova.servers.list()}

        for i in range(0, self.conf.instance_count):
            alarm_name = self.alarm_names[i]
            if alarm_name in alarms:
                continue
            vm_name = '%s%d' % (self.conf.instance_basename, i)
            vm_id = getattr(servers[vm_name], 'id')
            alarm_request = dict(
                name=alarm_name,
                description=u'VM failure',
                enabled=True,
                alarm_actions=[u'http://%s:%d/failure'
                               % (self.conf.consumer.ip,
                                  self.conf.consumer.port)],
                repeat_actions=False,
                severity=u'moderate',
                type=u'event',
                event_rule=dict(
                    event_type=u'compute.instance.update',
                    query=[
                        dict(field=u'traits.instance_id',
                             type='',
                             op=u'eq',
                             value=vm_id),
                        dict(field=u'traits.state',
                             type='',
                             op=u'eq',
                             value=u'error')]))
            self.aodh.alarm.create(alarm_request)

        self.log.info('alarm create end......')

    def delete(self):
        self.log.info('alarm delete start.......')

        alarms = {alarm['name']: alarm for alarm in self.aodh.alarm.list()}
        for alarm_name in self.alarm_names:
            if alarm_name in alarms:
                self.aodh.alarm.delete(alarms[alarm_name]['alarm_id'])

        del self.alarm_names[:]

        self.log.info('alarm delete end.......')
