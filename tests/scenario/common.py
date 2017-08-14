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

    reg = re.compile(regex)
    result = reg.match(full_path)
    return result.group(0)


def calculate_notification_time():
    log_file = '{0}/{1}'.format(sys.path[0], 'doctor.log')

    reg = '(?<=doctor monitor detected at)\d.\d'
    detected = match_rep_in_file(reg, log_file)

    reg = '(?<=doctor consumer notified at)\d.\d'
    notified = match_rep_in_file(reg, log_file)

    return detected - notified