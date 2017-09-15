##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from flask import Flask
from flask import request
import json
import time
from threading import Thread
import requests

from doctor_tests.consumer.base import BaseConsumer


class SampleConsumer(BaseConsumer):

    def __init__(self, conf, log):
        super(SampleConsumer, self).__init__(conf, log)
        self.app = None

    def start(self):
        self.log.info('sample consumer start......')
        self.app = ConsumerApp(self.conf.consumer.port, self, self.log)
        self.app.start()

    def stop(self):
        self.log.info('sample consumer stop......')
        if not self.app:
            return
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        url = 'http://%s:%d/shutdown'\
              % (self.conf.consumer.ip,
                 self.conf.consumer.port)
        requests.post(url, data='', headers=headers)


class ConsumerApp(Thread):

    def __init__(self, port, consumer, log):
        Thread.__init__(self)
        self.port = port
        self.consumer = consumer
        self.log = log

    def run(self):
        app = Flask('consumer')

        @app.route('/failure', methods=['POST'])
        def event_posted():
            self.log.info('doctor consumer notified at %s' % time.time())
            self.log.info('sample consumer received data = %s' % request.data)
            data = json.loads(request.data.decode('utf8'))
            return 'OK'

        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            self.log.info('shutdown consumer app server at %s' % time.time())
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return 'consumer app shutting down...'

        app.run(host="0.0.0.0", port=self.port)
