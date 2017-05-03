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

from identity_auth import get_session
import logger as doctor_log
from os_clients import keystone_client
from os_clients import nova_client


OPTS = [
    cfg.StrOpt('user',
               default='doctor',
               help='the name of test user',
               required=True),
    cfg.StrOpt('password',
               default='doctor',
               help='the password of test user',
               required=True),
    cfg.StrOpt('project',
               default='doctor',
               help='the name of test project',
               required=True),
    cfg.StrOpt('role',
               default='_member_',
               help='the role of test user',
               required=True),
    cfg.IntOpt('vm_count',
               default=os.environ.get('VM_COUNT', 1),
               help='the num of test vm',
               required=True),
]

LOG = doctor_log.Logger('doctor').getLogger()


class User(object):

    def __init__(self, conf):
        self.conf = conf
        self.keystone = \
            keystone_client(get_session())
        self.nova = \
            nova_client(conf.nova_version, get_session())
        self.users = {}
        self.projects = {}
        self.roles = {}
        self.roles_for_user = {}
        self.roles_for_admin = {}

    def create(self):
        """create test user, project and etc"""
        LOG.info('user create start......')

        self._create_project()
        self._create_user()
        self._create_role()
        self._add_user_role_in_project(is_admin=False)
        self._add_user_role_in_project(is_admin=True)

    def _create_project(self):
        """create test project"""
        self.projects = {project.name: project
                    for project in self.keystone.tenants.list()}
        if self.conf.project not in self.projects:
            test_project = \
                self.keystone.tenants.create(self.conf.project)
            self.projects[test_project.name] = test_project

    def _create_user(self):
        """create test user"""
        project = self.projects.get(self.conf.project)
        self.users = {user.name: user for user in self.keystone.users.list()}
        if self.conf.user not in self.users:
            test_user = self.keystone.users.create(
                self.conf.user,
                password=self.conf.password,
                tenant_id=project.id)
            self.users[test_user.name] = test_user

    def _create_role(self):
        """create test role"""
        self.roles = {role.name: role for role in self.keystone.roles.list()}
        if self.conf.role not in self.roles:
            test_role = self.keystone.roles.create(self.conf.role)
            self.roles[test_role.name] = test_role

    def _add_user_role_in_project(self, is_admin=False):
        """add test user with test role in test project"""
        project = self.projects.get(self.conf.project)

        user_name = 'admin' if is_admin else self.conf.user
        user = self.users.get(user_name)

        role_name = 'admin' if is_admin else self.conf.role
        role = self.roles.get(role_name)

        roles_for_user = self.roles_for_admin \
            if is_admin else self.roles_for_user

        roles_for_user = \
            {role.name: role for role in
             self.keystone.roles.roles_for_user(user, tenant=project)}
        if role_name not in roles_for_user:
            self.keystone.roles.add_user_role(user, role, tenant=project)
            roles_for_user[role_name] = role

    def delete(self):
        """delete the test user, project and role"""
        project = self.projects.get(self.conf.project)
        user = self.users.get(self.conf.user)
        role = self.roles.get(self.conf.role)

        if project:
            if 'admin' in self.roles_for_admin:
                self.keystone.roles.remove_user_role(
                    self.users['admin'],
                    self.roles['admin'],
                    tenant=project)

            if user:
                if role and self.conf.role in self.roles_for_user:
                    self.keystone.roles.remove_user_role(
                        user, role, tenant=project)
                    self.keystone.roles.delete()
                self.keystone.users.delete()

            self.keystone.tenants.delete(project)

    def update_quota(self):
        project = self.projects.get(self.conf.project)
        user = self.users.get(self.conf.user)

        if project and user:
            self.quota = self.nova.quotas.get(project.id,
                                              user_id=user.id)
            if self.conf.vm_count > self.quota.instances:
                self.nova.quotas.update(project.id,
                                        instances=self.conf.vm_count,
                                        user_id=user.id)
            if self.conf.vm_count > self.quota.cores:
                self.nova.quotas.update(project.id,
                                        cores=self.conf.vm_count,
                                        user_id=user.id)
        else:
            raise Exception('No project or role for update quota')
