#!/bin/bash
set -eux

node_id=$(fuel node |grep controller | awk '{print "node-"$1}')
for i in $node_id;do
    ssh $i "sed -i 's|- notifier://?topic=alarm.all|- notifier://|' /etc/ceilometer/event_pipeline.yaml; service ceilometer-agent-notification restart"
done

exit 0
