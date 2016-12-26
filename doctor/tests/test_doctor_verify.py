##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from oslotest import base

from doctor import service
from doctor.consumer.base import get_consumer
from doctor.monitor.base import get_monitor
from doctor.inspector.base import get_inspector
from doctor.installer.base import get_installer


class DoctorTest(base.BaseTestCase):

    def setUp(self):
        self.conf = service.prepare_service()
        self.installer = get_installer(self.conf)
        self.inspector = get_inspector(self.conf)
        self.monitor = get_monitor(self.conf)
        self.consumer = get_consumer(self.conf)

    def test_doctor_verify(self):

        self.installer.prepare_ssh_to_cloud()
        self.installer.prepare_test_env()

        self.inpector.start()

        self.monitor.start()

        self.consumer.start()

    def download_image():
        pass

    def upload_image_to_cloud():
        pass

    def create_doctor_user():
        pass

    def boot_test_vm():
        pass

    def create_test_alarm():
        pass

    def tearDown(self):
        self.inspector.stop()
        self.monitor.stop()
        self.consumer.stop()

