import os
import sys
import urllib2

import logger as doctor_log
import os_clients
import service

LOG = doctor_log.Logger('doctor_inspector').getLogger()


class DoctorTest(object):

    def __init__(self, conf):
        self.conf = conf
        self.session = os_clients.get_session(conf)
        self._init_os_clients()

    def _init_os_clients(self):
        self.os_clients = {
            "nova": os_clients.nova_client(self.conf, self.session),
            "glance": os_clients.glance_client(self.conf, self.session),
            "keystone": os_clients.keystone_client(self.conf, self.session)
        }

    def upload_image_to_cloud(self):
        self.use_existing_image = False
        glance_client = self.os_clients["glance"]
        images = {image.name: image for image in glance_client.images.list()}
        if self.conf.image.name not in images:
            if not os.path.exists(self.conf.image.file_name):
                resp = urllib2.urlopen(self.conf.image.url)
                with open(self.conf.image.file_name, "wb") as code:
                    code.write(resp.read())
            self.image = glance_client.images.create(name=self.conf.image.name,
                                                     disk_format=self.conf.image.format,
                                                     container_format="bare",
                                                     visibility="public")
            glance_client.images.upload(self.image['id'],
                                        open(self.conf.image.file_name, 'rb'))
        else:
            self.use_existing_image = True
            self.image = images[self.conf.image.name]

    def create_doctor_user(self):
        keystone_client = self.os_clients["keystone"]
        nova_client = self.os_clients["nova"]

        projects = {project.name: project for project in keystone_client.tenants.list()}
        self.project = projects[self.conf.test_project] if self.conf.test_project in projects \
            else keystone_client.tenants.create(self.conf.test_project)

        users = {user.name: user for user in keystone_client.users.list()}
        self.user = users[self.conf.test_user] if self.conf.test_user in users \
            else keystone_client.users.create(self.conf.test_user,
                                            password=self.conf.test_password,
                                            tenant_id=self.project['id'])

        roles = {role.name: role for role in keystone_client.roles.list()}
        self.role = roles[self.conf.role] if self.conf.role in roles \
            else keystone_client.roles.create(self.conf.role)

        roles_user = {role.name: role for role in
                      keystone_client.roles.roles_for_user(self.user,
                                                           tenant=self.project)}
        if self.conf.role not in roles_user:
            keystone_client.roles.add_user_role(self.user, self.role, tenant=self.project)

        quota = nova_client.quotas.get(self.conf.test_project)
        if self.conf.vm_count > quota.instances:
            nova_client.quotas.update(self.conf.test_project,
                                      instances=self.conf.vm_count,
                                      user_id=self.conf.test_user)
        if self.conf.vm_count > quota.cores:
            nova_client.quotas.update(self.conf.test_project,
                                      cores=self.conf.vm_count,
                                      user_id=self.conf.test_user)

    def run(self):
        # prepare the cloud env

        # preparing VM image...
        self.upload_image_to_cloud()

        # creating test user...
        self.create_doctor_user()

        # creating VM...

        # creating alarm...

        # starting doctor sample components...

        # injecting host failure...

        # verify the test results


def main():
    conf = service.prepare_service()

    doctor = DoctorTest(conf)
    doctor.run()


if __name__ == '__main__':
    sys.exit(main())