OpenStack NOVA API for marking host down.

Related Blueprints:

  https://blueprints.launchpad.net/nova/+spec/mark-host-down
  https://blueprints.launchpad.net/python-novaclient/+spec/support-force-down-service

What the API is for

  This API will give external fault monitoring system a possibility of telling
  OpenStack Nova fast that compute host is down. This will immediately enable
  calling of evacuation of any VM on host and further enabling faster HA
  actions.

What this API does

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

  request:
  PUT /v2.1/{tenant_id}/os-services/force-down
  {
  "binary": "nova-compute",
  "host": "host1",
  "forced_down": true
  }
  
  response:
  200 OK
  {
  "service": {
  "host": "host1",
  "binary": "nova-compute",
  "forced_down": true
  }
  }

  Example:
  curl -g -i -X PUT http://10.11.12.2:8774/v2.1/fd1e31d52912495d9136977f46a2dd
  67/os-services/force-down -H "Content-Type: application/json" -H "Accept: ap
  plication/json" -H "X-OpenStack-Nova-API-Version: 2.11" -H "X-Auth-Token: {S
  HA1}5521c2c0d456f142d8745921362a50d97c2269d6" -d '{"binary": "nova-compute",
  "host": "compute1.novalocal", "forced_down": true}'

CLI for forcing down:

  nova service-force-down <hostname> nova-compute
  
  Example:
  nova --service-type "computev21" service-force-down compute1.novalocal \
  nova-compute

REST API for disabling forced down:

  request:
  PUT /v2.1/{tenant_id}/os-services/force-down
  {
  "binary": "nova-compute",
  "host": "host1",
  "forced_down": false
  }
  
  response:
  200 OK
  {
  "service": {
  "host": "host1",
  "binary": "nova-compute",
  "forced_down": false
  }
  }
  
  Example:
  curl -g -i -X PUT http://10.11.12.2:8774/v2.1/fd1e31d52912495d9136977f46a2dd
  67/os-services/force-down -H "Content-Type: application/json" -H "Accept: ap
  plication/json" -H "X-OpenStack-Nova-API-Version: 2.11" -H "X-Auth-Token: {S
  HA1}5521c2c0d456f142d8745921362a50d97c2269d6" -d '{"binary": "nova-compute",
  "host": "compute1.novalocal", "forced_down": false}'

CLI for disabling forced down:
  nova service-force-down unset <hostname> nova-compute
  
  Example:
  nova --service-type "computev21" service-force-down --unset compute1.novalocal nova-compute
