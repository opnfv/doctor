##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os

from keystoneclient import exceptions as ks_exceptions
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
    cfg.StrOpt('doctor_domain_id',
               default=os.environ.get('OS_PROJECT_DOMAIN_ID', 'default'),
               help='the domain id of the doctor project',
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
        self.def_quota = None
        self.restore_def_quota = False
        self.keystone = keystone_client(
            self.conf.keystone_version, get_session())
        self.nova = nova_client(conf.nova_version, get_session())
        self.users = {}
        self.projects = {}
        self.roles = {}
        self.use_exist_role = False
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
        self.projects = {project.name: project for project in
                         self.keystone.projects.list(
                             domain=self.conf.doctor_domain_id)}
        if self.conf.doctor_project not in self.projects:
            self.log.info('create project......')
            test_project = self.keystone.projects.create(
                self.conf.doctor_project,
                self.conf.doctor_domain_id)
            self.projects[test_project.name] = test_project
        else:
            self.log.info('project %s already created......'
                          % self.conf.doctor_project)
        self.log.info('test project %s'
                      % str(self.projects[self.conf.doctor_project]))

    def _create_user(self):
        """create test user"""
        self.users = {user.name: user for user in
                      self.keystone.users.list(
                          domain=self.conf.doctor_domain_id)}
        if self.conf.doctor_user not in self.users:
            self.log.info('create user......')
            test_user = self.keystone.users.create(
                self.conf.doctor_user,
                password=self.conf.doctor_passwd,
                domain=self.conf.doctor_domain_id)
            self.users[test_user.name] = test_user
        else:
            self.log.info('user %s already created......'
                          % self.conf.doctor_user)
        self.log.info('test user %s'
                      % str(self.users[self.conf.doctor_user]))

    def _create_role(self):
        """create test role"""
        self.roles = {role.name: role for role in
                      self.keystone.roles.list()}
        if self.conf.doctor_role not in self.roles:
            self.log.info('create role......')
            test_role = self.keystone.roles.create(
                self.conf.doctor_role)
            self.roles[test_role.name] = test_role
        else:
            self.use_exist_role = True
            self.log.info('role %s already created......'
                          % self.conf.doctor_role)
        self.log.info('test role %s' % str(self.roles[self.conf.doctor_role]))

    def _add_user_role_in_project(self, is_admin=False):
        """add test user with test role in test project"""
        project = self.projects.get(self.conf.doctor_project)

        user_name = 'admin' if is_admin else self.conf.doctor_user
        user = self.users.get(user_name)

        role_name = 'admin' if is_admin else self.conf.doctor_role
        role = self.roles.get(role_name)

        roles_for_user = self.roles_for_admin \
            if is_admin else self.roles_for_user

        try:
            self.keystone.roles.check(role, user=user, project=project)
            self.log.info('Already grant a role:%s to user: %s on'
                          ' project: %s'
                          % (role_name, user_name,
                             self.conf.doctor_project))
        except ks_exceptions.NotFound:
            self.keystone.roles.grant(role, user=user, project=project)
            roles_for_user[role_name] = role

    def _restore_default_quota(self):
        if self.def_quota is not None and self.restore_def_quota:
            self.log.info('restore default quota......')
            self.nova.quota_classes.update('default',
                                           instances=self.def_quota.instances,
                                           cores=self.def_quota.cores)

    def delete(self):
        """delete the test user, project and role"""
        self.log.info('user delete start......')

        project = self.projects.get(self.conf.doctor_project)
        user = self.users.get(self.conf.doctor_user)
        role = self.roles.get(self.conf.doctor_role)

        self._restore_default_quota()

        if project:
            if 'admin' in self.roles_for_admin:
                self.keystone.roles.revoke(
                    self.roles['admin'],
                    user=self.users['admin'],
                    project=project)

            if user:
                if role and self.conf.doctor_role in self.roles_for_user:
                    self.keystone.roles.revoke(
                        role, user=user, project=project)
                    if not self.use_exist_role:
                        self.keystone.roles.delete(role)
                self.keystone.users.delete(user)

            self.keystone.projects.delete(project)
        self.log.info('user delete end......')

    def update_quota(self, instances=None, cores=None):
        self.log.info('quota update start......')
        project = self.projects.get(self.conf.doctor_project)

        user = self.users.get(self.conf.doctor_user)

        if instances is not None:
            quota_instances = instances
        else:
            quota_instances = self.conf.quota_instances
        if cores is not None:
            quota_cores = cores
        else:
            quota_cores = self.conf.quota_cores

        if project and user:
            # default needs to be at least the same as with doctor_user
            self.log.info('default quota update start......')

            self.def_quota = self.nova.quota_classes.get('default')
            if quota_instances > self.def_quota.instances:
                self.restore_def_quota = True
                self.nova.quota_classes.update('default',
                                               instances=quota_instances)
            if quota_cores > self.def_quota.cores:
                self.restore_def_quota = True
                self.nova.quota_classes.update('default',
                                               cores=quota_cores)
            self.log.info('user quota update start......')
            self.quota = self.nova.quotas.get(project.id,
                                              user_id=user.id)
            if quota_instances > self.quota.instances:
                self.nova.quotas.update(project.id,
                                        instances=quota_instances,
                                        user_id=user.id)
            if quota_cores > self.quota.cores:
                self.nova.quotas.update(project.id,
                                        cores=quota_cores,
                                        user_id=user.id)
        else:
            raise Exception('No project or role for update quota')
        self.log.info('quota update end......')
