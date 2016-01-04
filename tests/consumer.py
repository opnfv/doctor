#
# Copyright 2016 NEC Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
from flask import Flask
from flask import request
import json
import os
import time


app = Flask(__name__)


@app.route('/failure', methods=['POST'])
def event_posted():
    app.logger.debug('doctor consumer notified at %s' % time.time())
    app.logger.debug('received data = %s' % request.data)
    d = json.loads(request.data)
    return "OK"


def get_args():
    parser = argparse.ArgumentParser(description='Doctor Sample Monitor')
    parser.add_argument('port', metavar='PORT', type=int, nargs='?',
                        help='a port for inspectpr')
    return parser.parse_args()


def main():
    args = get_args()
    app.run(port=args.port, debug=True)


if __name__ == '__main__':
    main()
