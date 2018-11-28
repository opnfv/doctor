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
    for nova_file_bak in ["/var/lib/config-data/puppet-generated/nova_libvirt/etc/nova/nova.bak",  # noqa
                          "/var/lib/config-data/puppet-generated/nova/etc/nova/nova.bak",  # noqa
                          "/etc/nova/nova.bak"]:
        if os.path.isfile(nova_file_bak):
            nova_file = nova_file_bak.replace(".bak", ".conf")
            print('restoring nova.bak.')
            shutil.copyfile(nova_file_bak, nova_file)
            os.remove(nova_file_bak)
            return
    print('nova.bak does not exist.')
    return

restore_cpu_allocation_ratio()
