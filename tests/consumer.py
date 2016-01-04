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
