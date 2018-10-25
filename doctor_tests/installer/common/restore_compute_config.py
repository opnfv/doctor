##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import shutil


def restore_cpu_allocation_ratio():
    nova_base = "/var/lib/config-data/puppet-generated/nova"
    if not os.path.isdir(nova_base):
        nova_base = ""
    nova_file = nova_base + '/etc/nova/nova.conf'
    nova_file_bak = nova_base + '/etc/nova/nova.bak'

    if not os.path.isfile(nova_file_bak):
        print('Bak_file:%s does not exist.' % nova_file_bak)
    else:
        print('restore: %s' % nova_file)
        shutil.copyfile(nova_file_bak, nova_file)
        os.remove(nova_file_bak)
    return

restore_cpu_allocation_ratio()
