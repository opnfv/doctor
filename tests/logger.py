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


class Logger:
    def __init__(self, logger_name):

        CI_DEBUG = os.getenv('CI_DEBUG')

        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = 0
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(filename)s %(lineno)d '
                                      '%(name)-12s %(levelname)-8s %(message)s')
 
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        if CI_DEBUG is not None and CI_DEBUG.lower() == "true":
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        self.logger.addHandler(ch)

        file_handler = logging.FileHandler(logger_name)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)


    def getLogger(self):
        return self.logger

