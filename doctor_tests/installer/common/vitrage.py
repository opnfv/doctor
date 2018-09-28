##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os


vi_base = "/var/lib/config-data/puppet-generated/vitrage"
if not os.path.isdir(vi_base):
    vi_base = ""
vitrage_template_file = \
    vi_base + '/etc/vitrage/templates/vitrage_host_down_scenarios.yaml'

template = """
metadata:
 name: host_down_scenarios
 description: scenarios triggered by Doctor monitor 'compute.host.down' alarm
definitions:
 entities:
  - entity:
     category: ALARM
     name: compute.host.down
     template_id: host_down_alarm
  - entity:
     category: ALARM
     type: vitrage
     name: Instance Down
     template_id: instance_alarm
  - entity:
     category: RESOURCE
     type: nova.instance
     template_id: instance
  - entity:
     category: RESOURCE
     type: nova.host
     template_id: host
 relationships:
  - relationship:
     source: host_down_alarm
     relationship_type: on
     target: host
     template_id : host_down_alarm_on_host
  - relationship:
     source: host
     relationship_type: contains
     target: instance
     template_id : host_contains_instance
  - relationship:
     source: instance_alarm
     relationship_type: on
     target: instance
     template_id : alarm_on_instance
scenarios:
 - scenario:
    condition: host_down_alarm_on_host
    actions:
     - action:
        action_type: set_state
        action_target:
         target: host
        properties:
         state: ERROR
     - action:
        action_type: mark_down
        action_target:
         target: host
 - scenario:
    condition: host_down_alarm_on_host and host_contains_instance
    actions:
     - action:
        action_type: raise_alarm
        action_target:
         target: instance
        properties:
         alarm_name: Instance Down
         severity: critical
 - scenario:
    condition: host_down_alarm_on_host and host_contains_instance and alarm_on_instance
    actions:
     - action:
        action_type: add_causal_relationship
        action_target:
         source: host_down_alarm
         target: instance_alarm
     - action:
        action_type: mark_down
        action_target:
          target: instance
"""    # noqa


def set_vitrage_host_down_template():
    if os.path.isfile(vitrage_template_file):
        print('Vitrage host_down template file: %s already exists.'
              % vitrage_template_file)
    else:
        print('Create Vitrage host_down template file:%s.'
              % vitrage_template_file)
        with open(vitrage_template_file, 'w') as file:
            file.write(template)
