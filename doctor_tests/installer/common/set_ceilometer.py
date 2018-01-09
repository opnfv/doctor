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


set_notifier_topic()
