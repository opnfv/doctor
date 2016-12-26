##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

class CongressInspector(Inspector):

    def __init__(self):
        super(CongressInspector, self).__init__(conf)
        self.inspector_url = get_inspector_url()

    def get_inspector_url(self):
        return inspector_url

    def start(self):
        self.setup_rules()

    def stop(self):    
        self._del_rule(host_down, classification)

    def setup_rules(self):
        self._add_rule(name, policy, rule)

    def _add_rule(self, name, policy, rule):

    def _del_rule(self, name, policy):
