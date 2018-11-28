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


def set_cpu_allocation_ratio():
    nova_file_bak = None
    for nova_file in ["/var/lib/config-data/puppet-generated/nova_libvirt/etc/nova/nova.conf",
                      "/var/lib/config-data/puppet-generated/nova/etc/nova/nova.conf",
                      "/etc/nova/nova.conf"]:
        if os.path.isfile(nova_file):
            nova_file_bak = nova_file.replace(".conf",".bak")
            break

    if nova_file_bak == None:
        raise Exception("Could not find nova.conf")
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

set_cpu_allocation_ratio()
