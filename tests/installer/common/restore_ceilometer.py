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


restore_ep_config()
