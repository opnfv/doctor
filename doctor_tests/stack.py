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
        self.stack_name = None
        self.stack_id = None
        self.template = None
        self.parameters = {}
        self.files = {}

    # standard yaml.load will not work for hot tpl becasue of date format in
    # heat_template_version is not string
    def get_hot_tpl(self, template_file):
        if not os.path.isfile(template_file):
            raise Exception('File(%s) does not exist' % template_file)
        return get_template_contents(template_file=template_file)

    def _wait_stack_action_complete(self, action):
        action_in_progress = '%s_IN_PROGRESS' % action
        action_complete = '%s_COMPLETE' % action
        action_failed = '%s_FAILED' % action

        status = action_in_progress
        stack_retries = 160
        while status == action_in_progress and stack_retries > 0:
            time.sleep(2)
            try:
                stack = self.heat.stacks.get(self.stack_name)
            except heat_excecption.HTTPNotFound:
                if action == 'DELETE':
                    # Might happen you never get status as stack deleted
                    status = action_complete
                    break
                else:
                    raise Exception('unable to get stack')
            status = stack.stack_status
            stack_retries = stack_retries - 1
        if stack_retries == 0 and status != action_complete:
            raise Exception("stack %s not completed within 5min, status:"
                            " %s" % (action, status))
        elif status == action_complete:
            self.log.info('stack %s %s' % (self.stack_name, status))
        elif status == action_failed:
            raise Exception("stack %s failed" % action)
        else:
            self.log.error('stack %s %s' % (self.stack_name, status))
            raise Exception("stack %s unknown result" % action)

    def wait_stack_delete(self):
        self._wait_stack_action_complete('DELETE')

    def wait_stack_create(self):
        self._wait_stack_action_complete('CREATE')

    def wait_stack_update(self):
        self._wait_stack_action_complete('UPDATE')

    def create(self, stack_name, template, parameters={}, files={}):
        self.stack_name = stack_name
        self.template = template
        self.parameters = parameters
        self.files = files
        stack = self.heat.stacks.create(stack_name=self.stack_name,
                                        files=files,
                                        template=template,
                                        parameters=parameters)
        self.stack_id = stack['stack']['id']
        try:
            self.wait_stack_create()
        except Exception:
            # It might not always work at first
            self.log.info('retry creating maintenance stack.......')
            self.delete()
            time.sleep(5)
            stack = self.heat.stacks.create(stack_name=self.stack_name,
                                            files=files,
                                            template=template,
                                            parameters=parameters)
            self.stack_id = stack['stack']['id']
            self.wait_stack_create()

    def update(self, stack_name, stack_id, template, parameters={}, files={}):
        self.heat.stacks.update(stack_name=stack_name,
                                stack_id=stack_id,
                                files=files,
                                template=template,
                                parameters=parameters)
        self.wait_stack_update()

    def delete(self):
        if self.stack_id is not None:
            self.heat.stacks.delete(self.stack_name)
            self.wait_stack_delete()
        else:
            self.log.info('no stack to delete')
