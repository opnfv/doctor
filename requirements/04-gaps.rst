Gap analysis in upstream projects
=================================

This section presents the findings of gaps on existing VIM platforms. The focus
was to identify gaps based on the features and requirements specified in Section
3.3. The analysis work performed resulted in the identification of gaps of which
are herein presented.

VIM Northbound Interface
------------------------

Immediate Notification
^^^^^^^^^^^^^^^^^^^^^^

* Type: 'deficienty in performance'
* Description

  + To-be

    - VIM has to notify unavailability of virtual resource (fault) to VIM user
      immediately.
    - Notification should be passed in '1 second' after fault detected/notified
      by VIM.
    - Also, the following conditions/requirement have to be met:

      - Only the user can receive notification of fault related to owned virtual
        resource(s).

  + As-is

    - OpenStack Metering 'Ceilometer' can notify unavailability of virtual
      resource (fault) to the owner of virtual resource based on alarm
      configuration by the user.

      - Ceilometer Alarm API:
        http://docs.openstack.org/developer/ceilometer/webapi/v2.html#alarms

    - Alarm notifications are triggered by alarm evaluator instead notification
      agents that might receive faults

      - Ceilometer Architecture:
        http://docs.openstack.org/developer/ceilometer/architecture.html#id1

    - Evaluation interval should be equal to or larger than configured pipeline
      interval for collection of underlying metrics.

      - https://github.com/openstack/ceilometer/blob/stable/juno/ceilometer/alarm/service.py#L38-42

    - The interval for collection has to be set large enough which depends on
      the size of the deployment and the number of metrics to be collected.
    - The interval may not be less than one second in even small deployments.
      The default value is 60 seconds.
    - Alternative: OpenStack has a message bus to publish system events.
      Operator can allow user to connect this, but there are no functions to
      filter out other events that should not be passed to the user or does not
      requested by the user.

  + Gap

    - Fault notifications cannot be received immediately by Ceilometer.

Maintenance Notification
^^^^^^^^^^^^^^^^^^^^^^^^

* Type: 'missing'
* Description

  + To-be

    - VIM has to notify unavailability of virtual resource triggered by NFVI
      maintenance to VIM user.
    - Also, the following conditions/requirements have to be met:

      - VIM should accept maintenance message from administrator and mark target
        physical resource "in maintenance".
      - Only the owner of virtual resource hosted by target physical resource
        can receive the notification that can trigger some process for
        applications which are running on the virtual resource (e.g. cut off
        VM).

    - As-is

      - OpenStack: None
      - AWS (just for study)

        - AWS provides API and CLI to view status of resource (VM) and to create
          instance status and system status alarms to notify you when an
          instance has a failed status check.
          http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instances-status-check_sched.html
        - AWS provides API and CLI to view scheduled events, such as a reboot or
          retirement, for your instances. Also, those events will be notified
          via e-mail.
          http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-system-instance-status-check.html

    - Gap

      - VIM user cannot receive maintenance notifications.

VIM Southbound interface
------------------------

Normalization of data collection models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Type: 'missing'
* Description

  + To-be

    - A normalized data format needs to be created to cope with the many data
      models from different monitoring solutions.

  + As-is

    - Data can be collected from many places (e.g. Zabbix, Nagios, Cacti,
      Zenoss). Although each solution establishes its own data models, no common
      data abstraction models exist in OpenStack.

  + Gap

    - Normalized data format does not exist.

OpenStack
---------

Ceilometer
^^^^^^^^^^

OpenStack offers a telemetry service, Ceilometer, for collecting measurements of
the utilization of physical and virtual resources [4]_. Ceilometer can collect a
number of metrics across multiple OpenStack components and watch for variations
and trigger alarms based upon on the collected data.

Scalability of fault aggregation
________________________________

* Type: 'scalability issue'
* Description

  + To-be

    - Be able to scale to a large deployment, where thousands of monitoring
      events per second need to be analyzed.

  + As-is

    - Performance issue when scaling to medium-sized deployments.

  + Gap

    - Ceilometer seems not suitable for monitoring medium and large scale NFVI
      deployments.

* Related blueprints

  + Usage of Zabbix for fault aggregation [10]_. Zabbix can support a much higher
    number of fault events (up to 15.000 events per second, but obviously also
    has some upper bound:
    http://blog.zabbix.com/scalable-zabbix-lessons-on-hitting-9400-nvps/2615/

  + Decentralized/hierarchical deployment with multiple instances, where one
    instance is only responsible for a small NFVI.

Monitoring of hardware and software
___________________________________

* Type: 'missing (lack of functionality)'
* Description

  + To-be

    - OpenStack (as VIM) should monitor various hardware and software in NFVI to
      handle faults on them by Ceilometer.
    - OpenStack may have monitoring functionality in itself and can be
      integrated with third party monitoring tools.
    - OpenStack need to be able to detect the faults listed in Section 3.5.

  - As-is

    - For each deployment of OpenStack, an operator has responsibility to
      configure monitoring tools with relevant scripts or plugins in order to
      monitor hardware and software.
    - OpenStack Ceilometer does not monitor hardware and software to capture
      faults.

    +	Gap

      - Ceilometer is not able to detect and handle all faults listed in Section
        3.5.

* Related blueprints / workarounds

  - Use other dedicated monitoring tools like Zabbix or Monasca

Nova
^^^^

OpenStack Nova [5]_ is a mature and widely known and used component in OpenStack
cloud deployments. It is the main part of an infrastructure as a service system
providing a cloud computing fabric controller, supporting a wide diversity of
virtualization and container technologies.

Nova has proven throughout these past years to be highly available and
fault-tolerant. Featuring its own API, it also provides a compatibility API with
Amazon EC2 APIs.

Fencing instances of an unreachable host
________________________________________

* Type: 'missing'
* Description

  + To-be

    - Safe VM evacuation has to be preceded by fencing (isolate, shut down) the
      failed host. Failing to do so -- when the perceived disconnection is due
      to some transient or partial failure -- the evacuation might lead into two
      identical instances running together and having a dangerous conflict.
    - Fencing Instances of an unreachable host:
      https://wiki.openstack.org/wiki/Fencing_Instances_of_an_Unreachable_Host

  + As-is

    - When a VM goes down due to a host HW, host OS or hypervisor failure,
      nothing happens in OpenStack. The VMs of a crashed host/hypervisor are
      reported to be live and OK through the OpenStack API.

  + Gap

    - OpenStack does not fence instances of an unreachable host.

* Related blueprints

  + https://blueprints.launchpad.net/nova/+spec/fencing


Evacuate VMs on Maintenance mode
________________________________

* Type: 'missing'
* Description

  + To-be

    - When maintenance mode for a compute host is set, trigger VM evacuation to
      available compute nodes before bringing the host down for maintenance.

  + As-is

    - If setting a compute node to a maintenance mode, OpenStack only schedules
      evacuation of all VMs to available compute nodes if in-maintenance compute
      node runs the XenAPI and VMware ESX hypervisors. Other hypervisors (e.g.
      KVM) are not supported and, hence, guest VMs will likely stop running due
      to maintenance actions administrator may perform (e.g. hardware upgrades,
      OS updates).

  + Gap

    - Nova libvirt hypervisor driver does not implement automatic guest VMs
      evacuation when compute nodes are set to maintenance mode (``$ nova
      host-update --maintenance enable <hostname>``).

Monasca
^^^^^^^

Monasca is an open-source monitoring-as-a-service (MONaaS) solution that
integrates with OpenStack. Even though it is still in its early days, it is the
interest of the community that the platform be multi-tenant, highly scalable,
performant and fault-tolerant. Companion with a streaming alarm engine and a
notification engine, is a northbound REST API users can use to interact with
Monasca. Hundreds of thousands of metrics per second can be processed [8]_.

Anomaly detection
_________________


* Type: 'missing (lack of functionality)'
* Description

  + To-be

    - Detect the failure and perform a root cause analysis to filter out other
      alarms that may be triggered due to their cascading relation.

  + As-is

    - A mechanism to detect root causes of failures is not available.

  + Gap

    - Certain failures can trigger many alarms due to their dependency on the
      underlying root cause of failure. Knowing the root cause can help filter
      out unnecessary and overwhelming alarms.

* Related blueprints / workarounds

  + Monasca as of now lacks this feature, although the community is aware and
    working toward supporting it.

Sensor monitoring
_________________

* Type: 'missing (lack of functionality)'
* Description

  + To-be

    - It should support monitoring sensor data retrieving, for instance, from
      IPMI.

  + As-is

    - Monasca does not monitor sensor data

  + Gap

    - Sensor monitoring is of the most importance. It provides operators status
      on the state of the physical infrastructure (e.g. temperature, fans).

* Related blueprints / workarounds

  + Monasca can be configured to use third-party monitoring solutions (e.g.
    Nagios, Cacti) for retrieving additional data.

Hardware monitoring tools
-------------------------

Zabbix
^^^^^^

Zabbix is an open-source solution for monitoring availability and performance of
infrastructure components (i.e. servers and network devices), as well as
applications [10]_. It can be customized for use with OpenStack. It is a mature
tool and has been proven to be able to scale to large systems with 100,000s of
devices.

Delay in execution of actions
_____________________________


* Type: 'deficiency in performance'
* Description

  + To-be

    - After detecting a fault, the monitoring tool should immediately execute
      the appropriate action, e.g. inform the manager through the NB I/F

  + As-is

    - A delay of around 10 seconds was measured in two independent testbed
      deployments

  + Gap

    - Cause of the delay needs to be identified and fixed

..
 vim: set tabstop=4 expandtab textwidth=80:
