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

    def run(self):
        # prepare the cloud env

        # preparing VM image...
        self.upload_image_to_cloud()

        # creating test user...

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