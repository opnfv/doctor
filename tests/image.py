##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import urllib2

from oslo_config import cfg

from identity_auth import get_session
from os_clients import glance_client
import logger as doctor_log

IMAGE_OPTS = [
    cfg.StrOpt('name',
               default=os.environ.get('IMAGE_NAME', 'cirros'),
               help='the name of test image',
               required=True),
    cfg.StrOpt('format',
               default='qcow2',
               help='the format of test image',
               required=True),
    cfg.StrOpt('file_name',
               default='cirros.img',
               help='the name of image file',
               required=True),
    cfg.StrOpt('url',
               default='https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img',
               help='the url where to get the image',
               required=True),
]

LOG = doctor_log.Logger('doctor').getLogger()


class Image(object):

    def __init__(self, conf):
        self.conf = conf
        self.glance = \
            glance_client(conf.os_clients.glance_version,
                          get_session())
        self.use_existing_image = False
        self.image = None

    def create(self):
        LOG.info('image create start......')

        images = {image.name: image for image in self.glance.images.list()}
        if self.conf.image.name not in images:
            if not os.path.exists(self.conf.image.file_name):
                resp = urllib2.urlopen(self.conf.image.url)
                with open(self.conf.image.file_name, "wb") as file:
                    file.write(resp.read())
            self.image = self.glance.images.create(name=self.conf.image.name,
                                                   disk_format=self.conf.image.format,
                                                   container_format="bare",
                                                   visibility="public")
            self.glance.images.upload(self.image['id'],
                                      open(self.conf.image.file_name, 'rb'))
        else:
            self.use_existing_image = True
            self.image = images[self.conf.image.name]

        LOG.info('image create end......')

    def delete(self):
        LOG.info('image delete start.......')

        if not self.use_existing_image and self.image:
            self.glance.images.delete(self.image['id'])

        LOG.info('image delete end.......')
