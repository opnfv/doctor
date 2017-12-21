##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


def set_doctor_driver_conf(ssh_client, restart_cmd):
    cg_set_cmd = '''#!/bin/bash
co_conf=/etc/congress/congress.conf
co_conf_bak=/etc/congress/congress.conf.bak
co_entry="congress.datasources.doctor_driver.DoctorDriver"
if sudo grep -e "^drivers.*$co_entry" $co_conf; then
    echo "NOTE: congress is configured as we needed"
else
    echo "modify the congress config"
    sudo cp $co_conf $co_conf_bak
    sudo sed -i -e "/^drivers/s/$/,$co_entry/"  $co_conf
    %s
fi
    ''' % (restart_cmd)

    ret, output = ssh_client.ssh(cg_set_cmd)
    if ret:
        raise Exception('Do the congress command in controller node failed...'
                        'ret=%s, cmd=%s, output=%s'
                        % (ret, cg_set_cmd, output))


def restore_doctor_driver_conf(ssh_client, restart_cmd):
    cg_restore_cmd = '''#!/bin/bash
co_conf=/etc/congress/congress.conf
co_conf_bak=/etc/congress/congress.conf.bak
if [ -e $co_conf_bak ]; then
    echo "restore the congress config"
    sudo cp $co_conf_bak $co_conf
    sudo rm $co_conf_bak
    %s
else
    echo "Do not need to restore the congress config"
fi
    ''' % (restart_cmd)

    ret, output = ssh_client.ssh(cg_restore_cmd)
    if ret:
        raise Exception('Do the congress command in controller node failed...'
                        'ret=%s, cmd=%s, output=%s'
                        % (ret, cg_restore_cmd, output))
