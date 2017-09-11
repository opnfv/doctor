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

from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import keystone_client
from doctor_tests.os_clients import nova_client


OPTS = [
    cfg.StrOpt('doctor_user',
               default='doctor',
               help='the name of test user',
               required=True),
    cfg.StrOpt('doctor_passwd',
               default='doctor',
               help='the password of test user',
               required=True),
    cfg.StrOpt('doctor_project',
               default='doctor',
               help='the name of test project',
               required=True),
    cfg.StrOpt('doctor_role',
               default='_member_',
               help='the role of test user',
               required=True),
    cfg.IntOpt('quota_instances',
               default=os.environ.get('VM_COUNT', 1),
               help='the quota of instances in test user',
               required=True),
    cfg.IntOpt('quota_cores',
               default=os.environ.get('VM_COUNT', 1),
               help='the quota of cores in test user',
               required=True),
]


class User(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
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
        self.log.info('user create start......')

        self._create_project()
        self._create_user()
        self._create_role()
        self._add_user_role_in_project(is_admin=False)
        self._add_user_role_in_project(is_admin=True)

        self.log.info('user create end......')

    def _create_project(self):
        """create test project"""
        self.projects = {project.name: project
                    for project in self.keystone.tenants.list()}
        if self.conf.doctor_project not in self.projects:
            test_project = \
                self.keystone.tenants.create(self.conf.doctor_project)
            self.projects[test_project.name] = test_project

    def _create_user(self):
        """create test user"""
        project = self.projects.get(self.conf.doctor_project)
        self.users = {user.name: user for user in self.keystone.users.list()}
        if self.conf.doctor_user not in self.users:
            test_user = self.keystone.users.create(
                self.conf.doctor_user,
                password=self.conf.doctor_passwd,
                tenant_id=project.id)
            self.users[test_user.name] = test_user

    def _create_role(self):
        """create test role"""
        self.roles = {role.name: role for role in self.keystone.roles.list()}
        if self.conf.doctor_role not in self.roles:
            test_role = self.keystone.roles.create(self.conf.doctor_role)
            self.roles[test_role.name] = test_role

    def _add_user_role_in_project(self, is_admin=False):
        """add test user with test role in test project"""
        project = self.projects.get(self.conf.doctor_project)

        user_name = 'admin' if is_admin else self.conf.doctor_user
        user = self.users.get(user_name)

        role_name = 'admin' if is_admin else self.conf.doctor_role
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
        self.log.info('user delete start......')

        project = self.projects.get(self.conf.doctor_project)
        user = self.users.get(self.conf.doctor_user)
        role = self.roles.get(self.conf.doctor_role)

        if project:
            if 'admin' in self.roles_for_admin:
                self.keystone.roles.remove_user_role(
                    self.users['admin'],
                    self.roles['admin'],
                    tenant=project)

            if user:
                if role and self.conf.doctor_role in self.roles_for_user:
                    self.keystone.roles.remove_user_role(
                        user, role, tenant=project)
                    self.keystone.roles.delete(role)
                self.keystone.users.delete(user)

            self.keystone.tenants.delete(project)
        self.log.info('user delete end......')

    def update_quota(self):
        self.log.info('user quota update start......')
        project = self.projects.get(self.conf.doctor_project)
        user = self.users.get(self.conf.doctor_user)

        if project and user:
            self.quota = self.nova.quotas.get(project.id,
                                              user_id=user.id)
            if self.conf.quota_instances > self.quota.instances:
                self.nova.quotas.update(project.id,
                                        instances=self.conf.quota_instances,
                                        user_id=user.id)
            if self.conf.quota_cores > self.quota.cores:
                self.nova.quotas.update(project.id,
                                        cores=self.conf.quota_cores,
                                        user_id=user.id)
            self.log.info('user quota update end......')
        else:
            raise Exception('No project or role for update quota')
