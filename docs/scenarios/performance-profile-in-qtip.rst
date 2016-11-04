.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


===================
Performance Profile
===================

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

The performance profile of Doctor scenario can be profiled in a time line[#f1]::

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

And a table[#f2] of components sorted by time cost from most to least

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

.. rubric:: Footnotes

.. [#f1] c/m = ceilometer
.. [#f2] Data in the table is for demonstration only, not actual measurement
