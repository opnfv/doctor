##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
try:
    from urllib.request import urlopen
except Exception:
    from urllib2 import urlopen


from oslo_config import cfg

from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import glance_client

OPTS = [
    cfg.StrOpt('image_name',
               default=os.environ.get('IMAGE_NAME', 'cirros'),
               help='the name of test image',
               required=True),
    cfg.StrOpt('image_format',
               default='qcow2',
               help='the format of test image',
               required=True),
    cfg.StrOpt('image_filename',
               default='cirros.img',
               help='the name of image file',
               required=True),
    cfg.StrOpt('image_download_url',
               default='https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img',  # noqa
               help='the url where to get the image',
               required=True),
]


class Image(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self.glance = \
            glance_client(conf.glance_version, get_session())
        self.use_existing_image = False
        self.image = None

    def create(self):
        self.log.info('image create start......')
        images = {image.name: image for image in self.glance.images.list()}
        if self.conf.image_name == 'cirros':
            cirros = [image for image in images if 'cirros' in image]
            if cirros:
                self.conf.image_name = cirros[0]
        if self.conf.image_name not in images:
            if not os.path.exists(self.conf.image_filename):
                resp = urlopen(self.conf.image_download_url)
                with open(self.conf.image_filename, "wb") as file:
                    file.write(resp.read())
            self.image = \
                self.glance.images.create(
                    name=self.conf.image_name,
                    disk_format=self.conf.image_format,
                    container_format="bare",
                    visibility="public")
            self.glance.images.upload(self.image['id'],
                                      open(self.conf.image_filename, 'rb'))
        else:
            self.use_existing_image = True
            self.image = images[self.conf.image_name]

        self.log.info('image create end......')

    def delete(self):
        self.log.info('image delete start.......')

        if not self.use_existing_image and self.image:
            self.glance.images.delete(self.image['id'])

        self.log.info('image delete end.......')
