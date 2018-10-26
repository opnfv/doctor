##############################################################################
# Copyright (c) 2018 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from six.moves import configparser
import os
import shutil


def set_drivers_config():
    co_base = "/var/lib/config-data/puppet-generated/congress"
    if not os.path.isdir(co_base):
        co_base = ""
    co_conf = co_base + "/etc/congress/congress.conf"
    co_conf_bak = co_base + "/etc/congress/congress.conf.bak"
    doctor_driver = "congress.datasources.doctor_driver.DoctorDriver"
    config_modified = False

    config = configparser.ConfigParser()
    config.read(co_conf)
    drivers = config.get('DEFAULT', 'drivers')

    if doctor_driver not in drivers:
        config_modified = True
        drivers += ',' + doctor_driver

    config.set('DEFAULT', 'drivers', drivers)

    if config_modified:
        shutil.copyfile(co_conf, co_conf_bak)
        with open(co_conf, 'w') as configfile:
            config.write(configfile)


set_drivers_config()
