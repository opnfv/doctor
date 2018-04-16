##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os

from oslo_config import cfg


OPTS = [
    cfg.StrOpt('test_case',
               default=os.environ.get('TEST_CASE', 'fault_management'),
               choices=['all', 'fault_management', 'maintenance'],
               help="A name of test case to be executed,"
                    " choices are 'all', 'fault_management' or 'maintenance'."
                    " Set 'all' to execute all the test cases existing in"
                    " this repo. Default is 'fault_management'. Another test"
                    " case can be specified only if a function named"
                    " test_<test_case>() was implemented in DoctorTest.",
               required=False),
]
