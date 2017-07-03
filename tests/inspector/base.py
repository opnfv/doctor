##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
class BaseInspector(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log

    def get_inspector_url(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass