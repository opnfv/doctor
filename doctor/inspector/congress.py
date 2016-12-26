##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from doctor.inspector.base import Inspector

class CongressInspector(Inspector):

    def __init__(self, conf):
        super(CongressInspector, self).__init__(conf)
        self.inspector_url = self.get_inspector_url()

    def get_inspector_url(self):
        return self.inspector_url

    def start(self):
        self.setup_rules()

    def stop(self):    
        self._del_rule()

    def setup_rules(self):
        self._add_rule()

    def _add_rule(self, name, policy, rule):
        pass

    def _del_rule(self, name, policy):
        pass
