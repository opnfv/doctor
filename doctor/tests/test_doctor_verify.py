##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import random
import urllib
import time

from oslotest import base

from doctor import service
import doctor.clients as os_client
from doctor.consumer.base import get_consumer
from doctor.monitor.base import get_monitor
from doctor.inspector.base import get_inspector
from doctor.installer.base import get_installer


class DoctorTest(base.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super(DoctorTest, cls).setUpClass()
        cls.conf = service.prepare_service()

        cls.installer = get_installer(cls.conf)
        cls.inspector = get_inspector(cls.conf)
        cls.monitor = get_monitor(cls.conf, cls.inspector)
        cls.consumer = get_consumer(cls.conf)

        cls.session = os_client.get_session(cls.conf)
        cls.nova = os_client.nova_client(cls.conf, cls.session)
        cls.glance = os_client.glance_client(cls.conf, cls.session)
        cls.keystone = os_client.keystone_client(cls.conf, cls.session)
        cls.ceilometer = os_client.ceilometer_client(cls.conf, cls.session)
        cls.doctor_session = os_client.get_session(cls.conf,
                                                   auth_url=cls.conf.keystone_auth.OS_AUTH_URL,
                                                   username=cls.conf.test_user,
                                                   password=cls.conf.test_password,
                                                   project_name=cls.conf.test_project)

    def upload_image_to_cloud(self):
        self.use_existing_image = False
        images = {image.name: image for image in self.nova.images.list()}
        if not self.conf.image.name in images:
            if not os.path.exists(self.conf.image.file_name):
                urllib.urlretrieve(self.conf.image.url, self.conf.image.file_name)
            self.image = self.glance.images.create(name=self.conf.image.name,
                                                   disk_format=self.conf.image.format,
                                                   container_format="bare",
                                                   visibility="public")
            self.glance.images.upload(self.image['id'],
                                      open(self.conf.image.file_name, 'rb'))
        else:
            self.use_existing_image = True
            self.image = images[self.conf.image.name]

    def create_doctor_user(self):
        projects = {project.name: project for project in self.keystone.tenants.list()}
        self.project = projects[self.conf.test_project] if self.conf.test_project in projects \
                else self.keystone.tenants.create(self.conf.test_project)

        users = {user.name: user for user in self.keystone.users.list()}
        self.user = users[self.conf.test_user] if self.conf.test_user in users \
            else self.keystone.users.create(self.conf.test_user,
                                            password=self.conf.test_password,
                                            tenant_id=self.project['id'])

        roles = {role.name: role for role in self.keystone.roles.list()}
        self.role = roles[self.conf.role] if self.conf.role in roles \
            else self.keystone.roles.create(self.conf.role)

        roles_user = {role.name: role for role in self.keystone.roles.roles_for_user(self.user, tenant=self.project)}
        if self.conf.role not in roles_user:
            self.keystone.roles.add_user_role(self.user, self.role, tenant=self.project)

        quota = self.nova.quotas.get(self.conf.test_project)
        if self.conf.vm_count > quota.instances:
            self.nova.quotas.update(self.conf.test_project,
                                    instances=self.conf.vm_count,
                                    user_id=self.conf.test_user)
        if self.conf.vm_count > quota.cores:
            self.nova.quotas.update(self.conf.test_project,
                                    cores=self.conf.vm_count,
                                    user_id=self.conf.test_user)

    def boot_test_vms(self):
        # test VM done with test user, so can test non-admin
        self.nova_under_doctor = os_client.nova_client(self.conf, session=self.doctor_session)
        self.servers = {}
        existing_servers = {server.name: server for server in self.nova_under_doctor.servers.list()}
        flavors = {flavor.name: flavor for flavor in self.nova.flavors.list()}
        for i in range(0, self.conf.vm_count):
            vm_name = "%s%d"%(self.conf.vm_name, i)
            self.servers[vm_name] = existing_servers[vm_name] if vm_name in existing_servers \
                else self.nova_under_doctor.servers.create(name=vm_name,
                                                           flavor=flavors[self.conf.vm_flavor],
                                                           image=self.image)

    def wait_for_vm_active(self):
        count = 0
        while count < 60:
            active_count = 0
            for server in self.servers.values():
                if "active" == server.state:
                    active_count += 1
                elif "error" == server.state:
                    return False
                else:
                    time.sleep(0)
                    count += 1
                    continue
            if active_count == self.conf.vm_count:
                return True
            count += 1
        return False

    def create_test_alarms(self):
        self.ceilometer_under_doctor = \
            os_client.ceilometer_client(self.conf, session=self.doctor_session)
        alarms = {alarm.name: alarm for alarm in self.ceilometer_under_doctor.alarms.list()}
        for i in range(0, self.conf.vm_count):
            alarm_name = "%s%d"%(self.conf.alarm_name, i)
            if alarm_name in alarms:
                continue;
            vm_name = "%s%d"%(self.conf.vm_name, i)
            vm_id = self.servers[vm_name].__dict__.get("id")
            alarm_request = dict(name=alarm_name,
                                 description=u'VM failure',
                                 enabled=True,
                                 alarm_action="http://localhost:%d/failure" % self.consumer.port,
                                 repeat_actions=False,
                                 severity='moderate',
                                 type=u'event',
                                 event_rule=dict(query=[
                                    dict(
                                        field=u'traits.instance_id',
                                        type='',
                                        op=u'eq',
                                        value=vm_id),
                                    dict(
                                        field=u'traits.state',
                                        type='',
                                        op=u'eq',
                                        value='error')],
                                    event_type='compute.instance.update'))
            self.ceilometer_under_doctor.alarms.create(**alarm_request)

    def disable_network_of_computer_host(self):
        num = random.randint(0, self.conf.vm_count)
        vm_name = "%s%d" % (self.conf.vm_name, num)
        compute_hostname = self.servers[vm_name].__dict__.get("OS-EXT-SRV-ATTR:host")
        compute_ip = self.installer.get_compute_ip_from_hostname(compute_hostname)


    def test_doctor_verify(self):

        # prepare the cloud env
        self.installer.prepare_ssh_to_cloud()
        self.installer.prepare_test_env()

        # preparing VM image...
        self.upload_image_to_cloud()

        # creating test user...
        self.create_doctor_user()

        # creating VM...
        self.boot_test_vms()
        self.assertTrue(self.wait_for_vm_active())

        # creating alarm...
        self.create_test_alarms()

        # starting doctor sample components...
        self.inspector.start()
        self.monitor.start()
        self.consumer.start()

        # injecting host failure...
        self.disable_network_of_computer_host()

        # verify the test results


    def tearDown(self):
        super(DoctorTest, self).tearDown()
        self.inspector.stop()
        self.monitor.stop()
        self.consumer.stop()

        if not self.use_existing_image:
            self.glance.images.delete(self.image['id'])

        for server in self.servers.values():
            self.nova_under_doctor.servers.delete(server)

        self.keystone.roles.remove_user_role(self.user, self.role, tenant=self.project)
        self.keystone.roles.delete(self.role)
        self.keystone.users.delete(self.user)
        self.keystone.tenants.delete(self.project)
