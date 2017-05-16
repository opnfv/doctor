##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os

from oslo_config import cfg

from identity_auth import get_identity_auth
from identity_auth import get_session
from os_clients import aodh_client
import logger as doctor_log
from os_clients import nova_client

OPTS = [
    cfg.StrOpt('alarm_basename',
               default='doctor_alarm',
               help='the base name of alarm',
               required=True),
]

LOG = doctor_log.Logger('doctor').getLogger()


class Alarm(object):

    def __init__(self, conf):
        self.conf = conf
        self.auth = get_identity_auth(username=self.conf.user,
                                      password=self.conf.password,
                                      project=self.conf.project_name)
        self.aodh = \
            aodh_client(conf.aodh_version,
                        get_session(auth=self.auth))
        self.nova = \
            nova_client(conf.nova_version,
                        get_session(auth=self.auth))
        self.alarms = {}
        self.alarm_names = []

    def create(self):
        LOG.info('alarm create start......')

        self.alarms = {alarm['name']: alarm for alarm in self.aodh.alarm.list()}
        servers = \
            {getattr(server, 'name'): server
             for server in self.nova.servers.list()}

        for i in range(0, self.conf.vm_count):
            alarm_name = '%s%d' % (self.conf.alarm_basename, i)
            self.alarm_names.append(alarm_name)
            if alarm_name in self.alarms:
                continue;
            vm_name = '%s%d' % (self.conf.vm_basename, i)
            vm_id = getattr(servers[vm_name], 'id')
            alarm_request = dict(
                name=alarm_name,
                description=u'VM failure',
                enabled=True,
                alarm_actions=[u'http://localhost:%d/failure' % self.conf.consumer.port],
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
            alarm = self.aodh.alarm.create(alarm_request)
            self.alarms[alarm_name] = alarm

        LOG.info('alarm create end......')

    def delete(self):
        LOG.info('alarm delete start.......')

        for alarm_name in self.alarm_names:
            if alarm_name in self.alarms:
                self.aodh.alarm.delete(self.alarms[alarm_name]['alarm_id'])

        LOG.info('alarm delete end.......')
