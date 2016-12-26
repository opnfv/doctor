##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from flask import Flask
from flask import request
import json
import logger as doctor_log
import time

from doctor.consumer.base import Consumer

LOG = doctor_log.Logger('doctor_consumer').getLogger()

app = Flask("consumer")

@app.route('/failure', methods=['POST'])
def event_posted():
    LOG.info('doctor consumer notified at %s' % time.time())
    LOG.info('received data = %s' % request.data)
    d = json.loads(request.data)
    return "OK"


class SampleConsumer(Consumer):
    global app

    def __init__(self, conf):
        super(SampleConsumer, self).__init__(conf)
        
    def start(self):
        app.run(host="0.0.0.0", port=self.consumer.port)

    def stop(self):
        pass


