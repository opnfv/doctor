##############################################################################
# Copyright (c) 2016 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

"""
PoC of performance profiler[1] for OPNFV doctor project

Usage:

Export environment variables to set timestamp at each checkpoint in millisecond.
Valid check points are: DOCTOR_PROFILER_T{00-09}

[1]: https://goo.gl/98Osig
"""

import os

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
host down:{T00}|      |      |      |          |        |      |      |      |
     raw failure:{T01}|      |      |          |        |      |      |      |
         found affected:{T02}|      |          |        |      |      |      |
              marked host down:{T03}|          |        |      |      |      |
                         set VM error:{T04}    |        |      |      |      |
                               notified VM error:{T05}  |      |      |      |
                                        transformed event:{T06}|      |      |
                                                 evaluated event:{T07}|      |
                                                            fired alarm:{T08}|
                                                                received alarm:{T09}
"""


def main():
    check_points = ["T{:02d}".format(i) for i in range(TOTAL_CHECK_POINTS)]
    module_map = {"M{:02d}".format(i):
                  (MODULE_CHECK_POINTS[i], MODULE_CHECK_POINTS[i + 1])
                  for i in range(len(MODULE_CHECK_POINTS) - 1)}

    # check point tags
    elapsed_ms = {cp: os.getenv("{}_{}".format(PREFIX, cp))
                  for cp in check_points}

    def format_tag(tag):
        return TAG_FORMAT.format(tag or '?')

    tags = {cp: format_tag(ms) for cp, ms in elapsed_ms.iteritems()}

    def time_cost(cp):
        if elapsed_ms[cp[0]] and elapsed_ms[cp[1]]:
            return int(elapsed_ms[cp[1]]) - int(elapsed_ms[cp[0]])
        else:
            return None

    # module time cost tags
    modules_cost_ms = {module: time_cost(cp)
                       for module, cp in module_map.iteritems()}

    tags.update({module: format_tag(cost)
                 for module, cost in modules_cost_ms.iteritems()})

    tags.update({'total': time_cost((check_points[0], check_points[-1]))})

    profile = TEMPLATE.format(**tags)

    print profile

if __name__ == '__main__':
    main()
