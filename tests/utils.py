##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import json
import os


def load_json_file(full_path):
    """Loads JSON from file
    :param target_filename:
    :return:
    """
    if not os.path.isfile(full_path):
        raise Exception('File(%s) does not exist' % full_path)

    with open(full_path, 'r') as file:
        return json.load(file)


def write_json_file(full_path, data):
    """write JSON from file
    :param target_filename:
    :return:
    """

    with open(full_path, 'w+') as file:
        file.write(json.dumps(data))

