##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
# Usage:
#  import doctor_logger
#  logger = doctor_logger.Logger("script_name").getLogger()
#  logger.info("message to be shown with - INFO - ")
#  logger.debug("message to be shown with - DEBUG -")

import logging
import os

from doctor_tests.common.utils import get_root_dir


class Logger(object):
    def __init__(self, logger_name):

        CI_DEBUG = os.getenv('CI_DEBUG')

        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = 0
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(filename)s %(lineno)d '
                                      '%(levelname)-6s %(message)s')

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        if CI_DEBUG is not None and CI_DEBUG.lower() == "true":
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        self.logger.addHandler(ch)

        test_dir = get_root_dir()
        self.filename = '{0}/{1}.log'.format(test_dir, logger_name)
        file_handler = logging.FileHandler(self.filename, mode='w')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def getLogger(self):
        return self.logger

    def getLogFilename(self):
        return self.filename
