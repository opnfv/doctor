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
    co_base = "/var/lib/config-data/puppet-generated/congress"
    if not os.path.isdir(co_base):
        co_base = ""
    co_conf = co_base + "/etc/congress/congress.conf"
    co_conf_bak = co_base + "/etc/congress/congress.conf.bak"

    if not os.path.isfile(co_conf_bak):
        print('Bak_file:%s does not exist.' % co_conf_bak)
    else:
        print('restore: %s' % co_conf)
        shutil.copyfile(co_conf_bak, co_conf)
        os.remove(co_conf_bak)
    return


restore_drivers_config()
