##############################################################################
# Copyright (c) 2018 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import configparser
import shutil


def set_drivers_config():
    co_conf = "/etc/congress/congress.conf"
    co_conf_bak = "/etc/congress/congress.conf.bak"

    doctor_driver = "congress.datasources.doctor_driver.DoctorDriver"
    keystone_driver = "congress.datasources.keystone_driver.KeystoneDriver"
    keystonev3_driver = "congress.datasources.keystonev3_driver.KeystoneV3Driver"   # noqa

    config_modified = False

    config = configparser.ConfigParser()
    config.read(co_conf)
    drivers = config['DEFAULT']['drivers']

    if keystone_driver in drivers:
        config_modified = True
        drivers = drivers.replace(keystone_driver, keystonev3_driver)

    if doctor_driver not in drivers:
        config_modified = True
        drivers += ',' + doctor_driver

    config['DEFAULT']['drivers'] = drivers

    if config_modified:
        shutil.copyfile(co_conf, co_conf_bak)
        with open(co_conf, 'w') as configfile:
            config.write(configfile)


set_drivers_config()
