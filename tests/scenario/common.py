##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import re
import sys


def match_rep_in_file(regex, full_path):
    if not os.path.isfile(full_path):
        raise Exception('File(%s) does not exist' % full_path)

    with open(full_path, 'r') as file:
        for line in file:
            result = re.search(regex, line)
            if result:
                return result.group(0)

    return None


def calculate_notification_time():
    log_file = '{0}/{1}'.format(sys.path[0], 'doctor.log')

    reg = '(?<=doctor monitor detected at )\d+.\d+'
    detected = match_rep_in_file(reg, log_file)
    if not detected:
        raise Exception('Can not find detected time')

    reg = '(?<=doctor consumer notified at )\d+.\d+'
    notified = match_rep_in_file(reg, log_file)
    if not notified:
        raise Exception('Can not find notified time')

    return float(notified) - float(detected)