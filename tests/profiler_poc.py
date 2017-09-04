##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

"""
PoC of performance profiler for OPNFV doctor project

Usage:

Export environment variables to set timestamp at each checkpoint in millisecond.
Valid check points are: DOCTOR_PROFILER_T{00-09}

See also: https://goo.gl/98Osig
"""

import json
import os

from oslo_config import cfg


OPTS = [
    cfg.StrOpt('profiler_type',
               default=os.environ.get('PROFILER_TYPE', 'poc'),
               help='the type of installer'),
]


OUTPUT = 'doctor_profiling_output'
PREFIX = 'DOCTOR_PROFILER'
TOTAL_CHECK_POINTS = 10
MODULE_CHECK_POINTS = ['T00', 'T01', 'T04', 'T05', 'T06', 'T09']
TAG_FORMAT = "{:<5}"
# Inspired by https://github.com/reorx/httpstat
TEMPLATE = """
Total time cost: {total}(ms)
==============================================================================>
       |Monitor|Inspector           |Controller|Notifier|Evaluator           |
       |{M00}  |{M01}               |{M02}     |{M03}   |{M04}               |
       |       |      |      |      |          |        |      |      |      |
link down:{T00}|      |      |      |          |        |      |      |      |
     raw failure:{T01}|      |      |          |        |      |      |      |
         found affected:{T02}|      |          |        |      |      |      |
                  set VM error:{T03}|          |        |      |      |      |
                         marked host down:{T04}|        |      |      |      |
                               notified VM error:{T05}  |      |      |      |
                                        transformed event:{T06}|      |      |
                                                 evaluated event:{T07}|      |
                                                            fired alarm:{T08}|
                                                                received alarm:{T09}
"""


def main(log=None):
    check_points = ["T{:02d}".format(i) for i in range(TOTAL_CHECK_POINTS)]
    module_map = {"M{:02d}".format(i):
                  (MODULE_CHECK_POINTS[i], MODULE_CHECK_POINTS[i + 1])
                  for i in range(len(MODULE_CHECK_POINTS) - 1)}

    # check point tags
    elapsed_ms = {cp: os.getenv("{}_{}".format(PREFIX, cp))
                  for cp in check_points}

    def format_tag(tag):
        return TAG_FORMAT.format(tag or '?')

    tags = {cp: format_tag(ms) for cp, ms in elapsed_ms.items()}

    def time_cost(cp):
        if elapsed_ms[cp[0]] and elapsed_ms[cp[1]]:
            return int(elapsed_ms[cp[1]]) - int(elapsed_ms[cp[0]])
        else:
            return None

    # module time cost tags
    modules_cost_ms = {module: time_cost(cp)
                       for module, cp in module_map.items()}

    tags.update({module: format_tag(cost)
                 for module, cost in modules_cost_ms.items()})

    tags.update({'total': time_cost((check_points[0], check_points[-1]))})

    profile = TEMPLATE.format(**tags)

    logfile = open('{}.json'.format(OUTPUT), 'w')
    logfile.write(json.dumps(tags))

    print(profile)
    if log:
        log.info('%s' % profile)


if __name__ == '__main__':
    main()
