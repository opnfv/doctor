##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import sys
from common.utils import match_rep_in_file


def calculate_notification_time():
    log_file = '{0}/{1}'.format(sys.path[0], 'doctor.log')

    reg = '(?<=doctor monitor detected at )\d+.\d+'
    result = match_rep_in_file(reg, log_file)
    if not result:
        raise Exception('Can not match detected time')
    detected = result.group(0)

    reg = '(?<=doctor consumer notified at )\d+.\d+'
    result = match_rep_in_file(reg, log_file)
    if not result:
        raise Exception('Can not match notified time')
    notified = result.group(0)

    return float(notified) - float(detected)