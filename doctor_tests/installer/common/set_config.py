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


cbase = "/var/lib/config-data/puppet-generated/ceilometer"
if not os.path.isdir(cbase):
    cbase = ""


def set_notifier_topic():
    ep_file = cbase + '/etc/ceilometer/event_pipeline.yaml'
    ep_file_bak = cbase + '/etc/ceilometer/event_pipeline.yaml.bak'
    event_notifier_topic = 'notifier://?topic=alarm.all'
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


def set_event_definitions():
    ed_file = cbase + '/etc/ceilometer/event_definitions.yaml'
    ed_file_bak = cbase + '/etc/ceilometer/event_definitions.bak'
    orig_ed_file_exist = True
    modify_config = False

    if not os.path.isfile(ed_file):
        # Deployment did not modify file, so it did not exist
        src_file = '/etc/ceilometer/event_definitions.yaml'
        if not os.path.isfile(src_file):
            config = []
            orig_ed_file_exist = False
        else:
            shutil.copyfile('/etc/ceilometer/event_definitions.yaml', ed_file)
    if orig_ed_file_exist:
        with open(ed_file, 'r') as file:
            config = yaml.safe_load(file)

    et_list = [et['event_type'] for et in config]

    if 'compute.instance.update' in et_list:
        print('NOTE: compute.instance.update allready configured')
    else:
        print('NOTE: add compute.instance.update to event_definitions.yaml')
        modify_config = True
        instance_update = {
            'event_type': 'compute.instance.update',
            'traits': {
                'deleted_at': {'fields': 'payload.deleted_at',
                               'type': 'datetime'},
                'disk_gb': {'fields': 'payload.disk_gb',
                            'type': 'int'},
                'display_name': {'fields': 'payload.display_name'},
                'ephemeral_gb': {'fields': 'payload.ephemeral_gb',
                                 'type': 'int'},
                'host': {'fields': 'publisher_id.`split(., 1, 1)`'},
                'instance_id': {'fields': 'payload.instance_id'},
                'instance_type': {'fields': 'payload.instance_type'},
                'instance_type_id': {'fields': 'payload.instance_type_id',
                                     'type': 'int'},
                'launched_at': {'fields': 'payload.launched_at',
                                'type': 'datetime'},
                'memory_mb': {'fields': 'payload.memory_mb',
                              'type': 'int'},
                'old_state': {'fields': 'payload.old_state'},
                'os_architecture': {
                    'fields':
                    "payload.image_meta.'org.openstack__1__architecture'"},
                'os_distro': {
                    'fields':
                    "payload.image_meta.'org.openstack__1__os_distro'"},
                'os_version': {
                    'fields':
                    "payload.image_meta.'org.openstack__1__os_version'"},
                'resource_id': {'fields': 'payload.instance_id'},
                'root_gb': {'fields': 'payload.root_gb',
                            'type': 'int'},
                'service': {'fields': 'publisher_id.`split(., 0, -1)`'},
                'state': {'fields': 'payload.state'},
                'tenant_id': {'fields': 'payload.tenant_id'},
                'user_id': {'fields': 'payload.user_id'},
                'vcpus': {'fields': 'payload.vcpus', 'type': 'int'}
                }
            }
        config.append(instance_update)

    if 'maintenance.scheduled' in et_list:
        print('NOTE: maintenance.scheduled allready configured')
    else:
        print('NOTE: add maintenance.scheduled to event_definitions.yaml')
        modify_config = True
        mscheduled = {
            'event_type': 'maintenance.scheduled',
            'traits': {
                'allowed_actions': {'fields': 'payload.allowed_actions'},
                'instance_ids': {'fields': 'payload.instance_ids'},
                'reply_url': {'fields': 'payload.reply_url'},
                'actions_at': {'fields': 'payload.actions_at',
                               'type': 'datetime'},
                'reply_at': {'fields': 'payload.reply_at', 'type': 'datetime'},
                'state': {'fields': 'payload.state'},
                'session_id': {'fields': 'payload.session_id'},
                'project_id': {'fields': 'payload.project_id'},
                'metadata': {'fields': 'payload.metadata'}
                }
            }
        config.append(mscheduled)

    if 'maintenance.host' in et_list:
        print('NOTE: maintenance.host allready configured')
    else:
        print('NOTE: add maintenance.host to event_definitions.yaml')
        modify_config = True
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

    if modify_config:
        if orig_ed_file_exist:
            shutil.copyfile(ed_file, ed_file_bak)
        else:
            with open(ed_file_bak, 'w+') as file:
                file.close()
        with open(ed_file, 'w+') as file:
            file.write(yaml.safe_dump(config))

set_notifier_topic()
set_event_definitions()
