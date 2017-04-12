##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
class BaseMonitor(object):
    """Monitor computer fault and report error to the inspector"""
    def __init__(self, conf, inspector_url):
        self.conf = conf
        self.inspector_url = inspector_url

    def start(self):
        pass

    def stop(self):
        pass
