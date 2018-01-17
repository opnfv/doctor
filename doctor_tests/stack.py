##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import time

from heatclient.common.template_utils import get_template_contents
from heatclient import exc as heat_excecption

from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import heat_client


class Stack(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        auth = get_identity_auth(project=self.conf.doctor_project)
        self.heat = heat_client(self.conf.heat_version,
                                get_session(auth=auth))
        self.stack = None
        self.stack_name = None

    # standard yaml.load will not work for hot tpl becasue of date format in
    # heat_template_version is not string
    def get_hot_tpl(self, template_file):
        if not os.path.isfile(template_file):
            raise Exception('File(%s) does not exist' % template_file)
        return get_template_contents(template_file=template_file)

    def wait_stack_delete(self):
        status = 'DELETE_IN_PROGRESS'
        stack_retries = 30
        while status == 'DELETE_IN_PROGRESS' and stack_retries > 0:
            time.sleep(2)
            try:
                stack = self.heat.stacks.get(self.stack_name)
            except heat_excecption.HTTPNotFound:
                self.log.info('stack deleted')
                return
            status = stack.stack_status
            stack_retries = stack_retries - 1
        if status != 'DELETE_COMPLETE':
            raise Exception("Stack deletion not completed within 60s, status:"
                            "%s" % status)

    def wait_stack_create(self):
        status = 'CREATE_IN_PROGRESS'
        stack_retries = 30
        while status == 'CREATE_IN_PROGRESS' and stack_retries > 0:
            time.sleep(2)
            try:
                stack = self.heat.stacks.get(self.stack_name)
            except Exception:
                raise Exception('unable to get stack')
            status = stack.stack_status
            stack_retries = stack_retries - 1
        if stack_retries == 0 and status != 'CREATE_COMPLETE':
            raise Exception("Stack creation not completed within 60s, status:"
                            " %s" % status)
        elif status == 'CREATE_COMPLETE':
            self.log.info('stack created')
        elif status == 'CREATE_FAILED':
            raise Exception("Stack creation failed")

    def create(self, stack_name, template, parameters={}, files={}):
        self.stack_name = stack_name
        self.stack = self.heat.stacks.create(stack_name=self.stack_name,
                                             files=files,
                                             template=template,
                                             parameters=parameters)
        self.wait_stack_create()

    def delete(self):
        if self.stack is not None:
            self.heat.stacks.delete(self.stack_name)
            self.wait_stack_delete()
