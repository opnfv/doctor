.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

=========================================
OpenStack NOVA API for marking host down.
=========================================

Related Blueprints:
===================

  https://blueprints.launchpad.net/nova/+spec/mark-host-down
  https://blueprints.launchpad.net/python-novaclient/+spec/support-force-down-service

What the API is for
===================

  This API will give external fault monitoring system a possibility of telling
  OpenStack Nova fast that compute host is down. This will immediately enable
  calling of evacuation of any VM on host and further enabling faster HA
  actions.

What this API does
==================

  In OpenStack the nova-compute service state can represent the compute host
  state and this new API is used to force this service down. It is assumed
  that the one calling this API has made sure the host is also fenced or
  powered down. This is important, so there is no chance same VM instance will
  appear twice in case evacuated to new compute host. When host is recovered
  by any means, the external system is responsible of calling the API again to
  disable forced_down flag and let the host nova-compute service report again
  host being up. If network fenced host come up again it should not boot VMs
  it had if figuring out they are evacuated to other compute host. The
  decision of deleting or booting VMs there used to be on host should be
  enhanced later to be more reliable by Nova blueprint:
  https://blueprints.launchpad.net/nova/+spec/robustify-evacuate

REST API for forcing down:
==========================

  Parameter explanations:
  tenant_id:       Identifier of the tenant.
  binary:          Compute service binary name.
  host:            Compute host name.
  forced_down:     Compute service forced down flag.
  token:           Token received after successful authentication.
  service_host_ip: Serving controller node ip.

  request:
  PUT /v2.1/{tenant_id}/os-services/force-down
  {
  "binary": "nova-compute",
  "host": "compute1",
  "forced_down": true
  }

  response:
  200 OK
  {
  "service": {
  "host": "compute1",
  "binary": "nova-compute",
  "forced_down": true
  }
  }

  Example:
  curl -g -i -X PUT http://{service_host_ip}:8774/v2.1/{tenant_id}/os-services
  /force-down -H "Content-Type: application/json" -H "Accept: application/json
  " -H "X-OpenStack-Nova-API-Version: 2.11" -H "X-Auth-Token: {token}" -d '{"b
  inary": "nova-compute", "host": "compute1", "forced_down": true}'

CLI for forcing down:
=====================

  nova service-force-down <hostname> nova-compute

  Example:
  nova service-force-down compute1 nova-compute

REST API for disabling forced down:
===================================

  Parameter explanations:
  tenant_id:       Identifier of the tenant.
  binary:          Compute service binary name.
  host:            Compute host name.
  forced_down:     Compute service forced down flag.
  token:           Token received after successful authentication.
  service_host_ip: Serving controller node ip.

  request:
  PUT /v2.1/{tenant_id}/os-services/force-down
  {
  "binary": "nova-compute",
  "host": "compute1",
  "forced_down": false
  }

  response:
  200 OK
  {
  "service": {
  "host": "compute1",
  "binary": "nova-compute",
  "forced_down": false
  }
  }

  Example:
  curl -g -i -X PUT http://{service_host_ip}:8774/v2.1/{tenant_id}/os-services
  /force-down -H "Content-Type: application/json" -H "Accept: application/json
  " -H "X-OpenStack-Nova-API-Version: 2.11" -H "X-Auth-Token: {token}" -d '{"b
  inary": "nova-compute", "host": "compute1", "forced_down": false}'

CLI for disabling forced down:
==============================

  nova service-force-down --unset <hostname> nova-compute

  Example:
  nova service-force-down --unset compute1 nova-compute
