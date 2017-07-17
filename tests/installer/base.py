##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
class BaseInstaller(object):
    def __init__(self, conf, log):
        self.conf = conf
        self.log = log

    def get_computer_user_name(self):
        pass

    def get_ssh_key_from_installer(self):
        pass

    def setup(self):
        pass

    def cleanup(self):
        pass
