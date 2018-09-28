##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import subprocess


def restore_aodh_event_alarm():
    # Remove modified docker and restore original
    orig = "orig_docker_id"
    new = "new_docker_id"
    if os.path.isfile(orig):
        with open("orig_docker_id", 'r') as oid:
            orig_docker_id = oid.read()
        oid.close()
        if os.path.isfile(new):
            with open("new_docker_id", 'r') as nid:
                new_docker_id = nid.read()
            nid.close()
            subprocess.check_output("docker stop %s" % new_docker_id,
                                    shell=True)
            subprocess.check_output("docker rm %s" % new_docker_id, shell=True)
            os.remove(new)
        subprocess.check_output("docker start %s" % orig_docker_id, shell=True)
        os.remove(orig)

restore_aodh_event_alarm()
