##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import shutil
import yaml

ep_file = '/etc/ceilometer/event_pipeline.yaml'
ep_file_bak = '/etc/ceilometer/event_pipeline.yaml.bak'
event_notifier_topic = 'notifier://?topic=alarm.all'


def set_notifier_topic():
    config_modified = False

    if not os.path.isfile(ep_file):
        raise Exception("File doesn't exist: %s." % ep_file)

    with open(ep_file, 'r') as file:
        config = yaml.safe_load(file)

    sinks = config['sinks']
    for sink in sinks:
        if sink['name'] == 'event_sink':
            publishers = sink['publishers']
            if event_notifier_topic not in publishers:
                print('Add event notifier in ceilometer')
                publishers.append(event_notifier_topic)
                config_modified = True
            else:
                print('NOTE: event notifier is configured'
                      'in ceilometer as we needed')

    if config_modified:
        shutil.copyfile(ep_file, ep_file_bak)
        with open(ep_file, 'w+') as file:
            file.write(yaml.safe_dump(config))


def set_maintenance_event_definitions():
    ed_file = '/etc/ceilometer/event_definitions.yaml'
    ed_file_bak = '/etc/ceilometer/event_definitions.bak'

    if not os.path.isfile(ed_file):
        raise Exception("File doesn't exist: %s." % ed_file)

    with open(ed_file, 'r') as file:
        config = yaml.safe_load(file)

    et_list = [et['event_type'] for et in config]

    if 'maintenance.scheduled' in et_list:
        add_mscheduled = False
        print('NOTE: maintenance.scheduled allready configured')
    else:
        print('NOTE: add maintenance.scheduled to event_definitions.yaml')
        add_mscheduled = True
        mscheduled = {
            'event_type': 'maintenance.scheduled',
            'traits': {
                'allowed_actions': {'fields': 'payload.allowed_actions'},
                'instance_ids': {'fields': 'payload.instance_ids'},
                'reply_url': {'fields': 'payload.reply_url'},
                'actions_at': {'fields': 'payload.actions_at',
                               'type': 'datetime'},
                'state': {'fields': 'payload.state'},
                'session_id': {'fields': 'payload.session_id'},
                'project_id': {'fields': 'payload.project_id'},
                'metadata': {'fields': 'payload.metadata'}
            }
        }
        config.append(mscheduled)

    if 'maintenance.host' in et_list:
        add_mhost = False
        print('NOTE: maintenance.host allready configured')
    else:
        print('NOTE: add maintenance.host to event_definitions.yaml')
        add_mhost = True
        mhost = {
            'event_type': 'maintenance.host',
            'traits': {
                'host': {'fields': 'payload.host'},
                'project_id': {'fields': 'payload.project_id'},
                'state': {'fields': 'payload.state'},
                'session_id': {'fields': 'payload.session_id'}
            }
        }
        config.append(mhost)

    if add_mscheduled or add_mhost:
        shutil.copyfile(ed_file, ed_file_bak)
        with open(ed_file, 'w+') as file:
            file.write(yaml.safe_dump(config))


def set_cpu_allocation_ratio():
    nova_file = '/etc/nova/nova.conf'
    nova_file_bak = '/etc/nova/nova.bak'

    if not os.path.isfile(nova_file):
        raise Exception("File doesn't exist: %s." % nova_file)
    # TODO (tojuvone): Unfortunately ConfigParser did not produce working conf
    fcheck = open(nova_file)
    found_list = ([ca for ca in fcheck.readlines() if "cpu_allocation_ratio"
                  in ca])
    fcheck.close()
    if found_list and len(found_list):
        change = False
        found = False
        for car in found_list:
            if car.startswith('#'):
                continue
            if car.startswith('cpu_allocation_ratio'):
                found = True
                if "1.0" not in car.split('=')[1]:
                    change = True
    if not found or change:
        # need to add or change
        shutil.copyfile(nova_file, nova_file_bak)
        fin = open(nova_file_bak)
        fout = open(nova_file, "wt")
        for line in fin:
            if change and line.startswith("cpu_allocation_ratio"):
                line = "cpu_allocation_ratio=1.0"
            if not found and line.startswith("[DEFAULT]"):
                line += "cpu_allocation_ratio=1.0\n"
            fout.write(line)
        fin.close()
        fout.close()

set_notifier_topic()
set_maintenance_event_definitions()
set_cpu_allocation_ratio()