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

ep_file = '/etc/ceilometer/event_pipeline.yaml'
ep_file_bak = '/etc/ceilometer/event_pipeline.yaml.bak'


def restore_ep_config():

    if not os.path.isfile(ep_file_bak):
        print('Bak_file:%s does not exist.' % ep_file_bak)
    else:
        print('restore')
        shutil.copyfile(ep_file_bak, ep_file)
        os.remove(ep_file_bak)
    return


def restore_ed_config():

    ed_file = '/etc/ceilometer/event_definitions.yaml'
    ed_file_bak = '/etc/ceilometer/event_definitions.bak'

    if not os.path.isfile(ed_file_bak):
        print("Bak_file doesn't exist: %s." % ed_file_bak)
    else:
        print('restore: %s' % ed_file)
        shutil.copyfile(ed_file_bak, ed_file)
        os.remove(ed_file_bak)
    return

restore_ep_config()
restore_ed_config()
