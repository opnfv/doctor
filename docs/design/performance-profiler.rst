.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


====================
Performance Profiler
====================

https://goo.gl/98Osig

This blueprint proposes to create a performance profiler for doctor scenarios.

Problem Description
===================

In the verification job for notification time, we have encountered some
performance issues, such as

1. In environment deployed by APEX, it meets the criteria while in the one by
Fuel, the performance is much more poor.
2. Signification performance degradation was spotted when we increase the total
number of VMs

It takes time to dig the log and analyse the reason. People have to collect
timestamp at each checkpoints manually to find out the bottleneck. A performance
profiler will make this process automatic.

Proposed Change
===============

Current Doctor scenario covers the inspector and notifier in the whole fault
management cycle::

  start                                          end
    +       +         +        +       +          +
    |       |         |        |       |          |
    |monitor|inspector|notifier|manager|controller|
    +------>+         |        |       |          |
  occurred  +-------->+        |       |          |
    |     detected    +------->+       |          |
    |       |     identified   +-------+          |
    |       |               notified   +--------->+
    |       |                  |    processed  resolved
    |       |                  |                  |
    |       +<-----doctor----->+                  |
    |                                             |
    |                                             |
    +<---------------fault management------------>+

The notification time can be split into several parts and visualized as a
timeline::

  start                                         end
    0----5---10---15---20---25---30---35---40---45--> (x 10ms)
    +    +   +   +   +    +      +   +   +   +   +
  0-hostdown |   |   |    |      |   |   |   |   |
    +--->+   |   |   |    |      |   |   |   |   |
    |  1-raw failure |    |      |   |   |   |   |
    |    +-->+   |   |    |      |   |   |   |   |
    |    | 2-found affected      |   |   |   |   |
    |    |   +-->+   |    |      |   |   |   |   |
    |    |     3-marked host down|   |   |   |   |
    |    |       +-->+    |      |   |   |   |   |
    |    |         4-set VM error|   |   |   |   |
    |    |           +--->+      |   |   |   |   |
    |    |           |  5-notified VM error  |   |
    |    |           |    +----->|   |   |   |   |
    |    |           |    |    6-transformed event
    |    |           |    |      +-->+   |   |   |
    |    |           |    |      | 7-evaluated event
    |    |           |    |      |   +-->+   |   |
    |    |           |    |      |     8-fired alarm
    |    |           |    |      |       +-->+   |
    |    |           |    |      |         9-received alarm
    |    |           |    |      |           +-->+
  sample | sample    |    |      |           |10-handled alarm
  monitor| inspector |nova| c/m  |    aodh   |
    |                                        |
    +<-----------------doctor--------------->+

Note: c/m = ceilometer

And a table of components sorted by time cost from most to least

+----------+---------+----------+
|Component |Time Cost|Percentage|
+==========+=========+==========+
|inspector |160ms    | 40%      |
+----------+---------+----------+
|aodh      |110ms    | 30%      |
+----------+---------+----------+
|monitor   |50ms     | 14%      |
+----------+---------+----------+
|...       |         |          |
+----------+---------+----------+
|...       |         |          |
+----------+---------+----------+

Note: data in the table is for demonstration only, not actual measurement

Timestamps can be collected from various sources

1. log files
2. trace point in code

The performance profiler will be integrated into the verification job to provide
detail result of the test. It can also be deployed independently to diagnose
performance issue in specified environment.

Working Items
=============

1. PoC with limited checkpoints
2. Integration with verification job
3. Collect timestamp at all checkpoints
4. Display the profiling result in console
5. Report the profiling result to test database
6. Independent package which can be installed to specified environment
