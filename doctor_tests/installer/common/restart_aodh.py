##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import socket
import subprocess


def restart_aodh_event_alarm():
    # Restart aodh-evaluator docker with localhost as controller host ip
    # This makes our alarm sending look the same as without container

    orig_docker_id = subprocess.check_output("docker ps | grep aodh-evaluator "
                                             "| awk '{print $1}'", shell=True)
    get_docker_startup = (
        'docker inspect --format=\'{{range .Config.Env}} -e "{{.}}" {{end}} '
        '{{range .Mounts}} -v {{.Source}}:{{.Destination}}{{if .Mode}}:'
        '{{.Mode}}{{end}}{{end}} -ti {{.Config.Image}}\''
    )
    docker_start = subprocess.check_output("%s %s" % (get_docker_startup,
                                           orig_docker_id), shell=True)
    with open("orig_docker_id", 'w') as oid:
        oid.write(orig_docker_id)
    oid.close()
    subprocess.check_output("docker stop %s" % orig_docker_id, shell=True)
    ip = socket.gethostbyname(socket.gethostname())

    ae_start = '-d --add-host="localhost:%s" %s' % (ip, docker_start)
    subprocess.check_output("docker run %s" % ae_start, shell=True)
    new_docker_id = subprocess.check_output("docker ps | grep aodh-evaluator "
                                            " | awk '{print $1}'", shell=True)
    if orig_docker_id == new_docker_id:
        raise Exception("Docker ids matching!")
    with open("new_docker_id", 'w') as nid:
        nid.write(new_docker_id)
    nid.close()

restart_aodh_event_alarm()
