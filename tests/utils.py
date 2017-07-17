##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import re
from os.path import isfile

def match_in_file(file, reg_exp):
    if isinstance(reg_exp, str):
        pattern = re.compile(reg_exp)
    else:
        raise Exception('the type of reg_exp(%s) is not str' % type(reg_exp))

    if isfile(file):
        with open(file, 'r') as f:
            data = f.read()
    else:
        raise Exception(' %s is not file' % file)

    return pattern.search(data)
