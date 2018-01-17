##############################################################################
# Copyright (c) 2018 Nokia Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from doctor_tests.common.utils import get_doctor_test_root_dir
from doctor_tests.identity_auth import get_identity_auth
from doctor_tests.identity_auth import get_session
from doctor_tests.os_clients import keystone_client
from doctor_tests.os_clients import neutron_client
from doctor_tests.os_clients import nova_client
from doctor_tests.stack import Stack


class Maintenance(object):

    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self.keystone = keystone_client(
            self.conf.keystone_version, get_session())
        self.nova = \
            nova_client(conf.nova_version, get_session())
        auth = get_identity_auth(project=self.conf.doctor_project)
        self.neutron = neutron_client(get_session(auth=auth))
        self.stack = Stack(self.conf, self.log)

    def get_external_network(self):
        ext_net = None
        networks = self.neutron.list_networks()['networks']
        for network in networks:
            if network['router:external']:
                ext_net = network['name']
                break
        if ext_net is None:
            raise Exception("externl network not defined")
        return ext_net

    def setup_maintenance(self, user):
        # each hypervisor needs to have same amount of vcpus and they
        # need to be free before test
        hvisors = self.nova.hypervisors.list(detailed=True)
        prev_vcpus = 0
        prev_hostname = ""
        self.log.info('checking hypervisors.......')
        for hvisor in hvisors:
            vcpus = hvisor.__getattr__("vcpus")
            vcpus_used = hvisor.__getattr__("vcpus_used")
            hostname = hvisor.__getattr__("hypervisor_hostname")
            if vcpus < 2:
                raise Exception('not enough vcpus on %s' % hostname)
            if vcpus_used > 0:
                raise Exception('%d vcpus used on %s'
                                % (vcpus_used, hostname))
            if prev_vcpus != 0 and prev_vcpus != vcpus:
                raise Exception('%d vcpus on %s does not match to'
                                '%d on %s'
                                % (vcpus, hostname,
                                   prev_vcpus, prev_hostname))
            prev_vcpus = vcpus
            prev_hostname = hostname

        # maintenance flavor made so that 2 instances take whole node
        flavor_vcpus = int(vcpus / 2)
        compute_nodes = len(hvisors)
        amount_actstdby_instances = 2
        amount_noredundancy_instances = 2 * compute_nodes - 2
        self.log.info('testing %d computes with %d vcpus each'
                      % (compute_nodes, vcpus))
        self.log.info('testing %d actstdby and %d noredundancy instances'
                      % (amount_actstdby_instances,
                         amount_noredundancy_instances))
        max_instances = (amount_actstdby_instances +
                         amount_noredundancy_instances)
        max_cores = compute_nodes * vcpus

        user.update_quota(max_instances, max_cores)

        test_dir = get_doctor_test_root_dir()
        template_file = '{0}/{1}'.format(test_dir, 'maintenance_hot_tpl.yaml')
        files, template = self.stack.get_hot_tpl(template_file)

        ext_net = self.get_external_network()

        parameters = {'ext_net': ext_net,
                      'flavor_vcpus': flavor_vcpus,
                      'maint_image': self.conf.image_name,
                      'nonha_intances': amount_noredundancy_instances,
                      'ha_intances': amount_actstdby_instances}

        self.log.info('creating maintenance stack.......')
        self.log.info('parameters: %s' % parameters)

        self.stack.create('doctor_test_maintenance',
                          template,
                          parameters=parameters,
                          files=files)

    def cleanup_maintenance(self):
        self.log.info('stack delete start.......')
        self.stack.delete()
