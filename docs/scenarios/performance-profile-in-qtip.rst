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

The performance profile of Doctor scenario is detailed as below::

  start                                          end
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

