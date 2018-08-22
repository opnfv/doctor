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


def restore_drivers_config():
    co_conf = "/etc/congress/congress.conf"
    co_conf_bak = "/etc/congress/congress.conf.bak"

    if not os.path.isfile(co_conf_bak):
        print('Bak_file:%s does not exist.' % co_conf_bak)
    else:
        print('restore: %s' % co_conf)
        shutil.copyfile(co_conf_bak, co_conf)
        os.remove(co_conf_bak)
    return


restore_drivers_config()
