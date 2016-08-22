#!/bin/bash -e
##############################################################################
# Copyright (c) 2016 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

[[ "${CI_DEBUG:-true}" == [Tt]rue ]] && set -x

cmd="python /home/opnfv/repos/functest/ci/run_tests.py -t doctor"
container_id=$(sudo docker ps -a | grep opnfv/functest | awk '{print $1}' | head -1)
sudo docker exec $container_id $cmd
