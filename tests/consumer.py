##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

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
    parser = argparse.ArgumentParser(description='Doctor Sample Consumer')
    parser.add_argument('host', metavar='HOST', type=int, nargs='?',
                        help='a host for consumer')
    parser.add_argument('port', metavar='PORT', type=int, nargs='?',
                        help='a port for consumer')
    return parser.parse_args()


def main():
    args = get_args()
    app.run(host=args.host, port=args.port, debug=True)


if __name__ == '__main__':
    main()
