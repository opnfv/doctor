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
from doctor_tests.os_clients import keystone_client
from doctor_tests.os_clients import vitrage_client

from doctor_tests.inspector.base import BaseInspector


class VitrageInspector(BaseInspector):

    def __init__(self, conf, log):
        super(VitrageInspector, self).__init__(conf, log)
        self.auth = get_identity_auth()
        self.keystone = keystone_client(get_session(auth=self.auth))
        self.vitrage = vitrage_client(self.conf.vitrage_version,
                                      get_session(auth=self.auth))
        self.inspector_url = self.get_inspector_url()

    def get_inspector_url(self):
        vitrage_endpoint = \
            self.keystone.session.get_endpoint(
                service_type='rca',
                interface='publicURL')
        return '%s/v1/event' % vitrage_endpoint

    def start(self):
        self.log.info('vitrage inspector start......')

    def stop(self):
        self.log.info('vitrage inspector stop......')
