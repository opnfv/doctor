##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import os
import shutil
import subprocess

from doctor_tests.installer.base import BaseInstaller
from doctor_tests.installer.common.vitrage import set_vitrage_host_down_template
from doctor_tests.common.constants import Inspector
from doctor_tests.common.utils import load_json_file
from doctor_tests.common.utils import write_json_file


class LocalInstaller(BaseInstaller):
    node_user_name = 'root'

    nova_policy_file = '/etc/nova/policy.json'
    nova_policy_file_backup = '%s%s' % (nova_policy_file, '.bak')

    def __init__(self, conf, log):
        super(LocalInstaller, self).__init__(conf, log)
        self.policy_modified = False
        self.add_policy_file = False

    def setup(self):
        self.get_ssh_key_from_installer()
        self.set_apply_patches()

    def cleanup(self):
        self.restore_apply_patches()

    def get_ssh_key_from_installer(self):
        self.log.info('Assuming SSH keys already exchanged with computer for local installer type')
        return None

    def get_host_ip_from_hostname(self, hostname):
        self.log.info('Get host ip from host name in local installer......')

        cmd = "getent hosts %s | awk '{ print $1 }'" % (hostname)
        server = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = server.communicate()
        host_ip = stdout.strip().decode("utf-8")

        self.log.info('Get host_ip:%s from host_name:%s in local installer' % (host_ip, hostname))
        return host_ip

    def set_apply_patches(self):
        self._set_nova_policy()
        if self.conf.inspector.type == Inspector.VITRAGE:
            set_vitrage_host_down_template()
            os.system('screen -S stack -p vitrage-graph -X stuff "^C^M^[[A^M"')

    def restore_apply_patches(self):
        self._restore_nova_policy()

    def _set_nova_policy(self):
        host_status_policy = 'os_compute_api:servers:show:host_status'
        host_status_rule = 'rule:admin_or_owner'
        policy_data = {
            'context_is_admin': 'role:admin',
            'owner': 'user_id:%(user_id)s',
            'admin_or_owner': 'rule:context_is_admin or rule:owner',
            host_status_policy: host_status_rule
        }

        if os.path.isfile(self.nova_policy_file):
            data = load_json_file(self.nova_policy_file)
            if host_status_policy in data:
                rule_origion = data[host_status_policy]
                if host_status_rule == rule_origion:
                    self.log.info('Do not need to modify nova policy.')
                    self.policy_modified = False
                else:
                    # update the host_status_policy
                    data[host_status_policy] = host_status_rule
                    self.policy_modified = True
            else:
                # add the host_status_policy, if the admin_or_owner is not
                # defined, add it also
                for policy, rule in policy_data.items():
                    if policy not in data:
                        data[policy] = rule
                self.policy_modified = True
            if self.policy_modified:
                self.log.info('Nova policy is Modified.')
                shutil.copyfile(self.nova_policy_file,
                                self.nova_policy_file_backup)
        else:
            # file does not exit, create a new one and add the policy
            self.log.info('Nova policy file not exist. Creating a new one')
            data = policy_data
            self.add_policy_file = True

        if self.policy_modified or self.add_policy_file:
            write_json_file(self.nova_policy_file, data)
            os.system('screen -S stack -p n-api -X stuff "^C^M^[[A^M"')

    def _restore_nova_policy(self):
        if self.policy_modified:
            shutil.copyfile(self.nova_policy_file_backup, self.nova_policy_file)
            os.remove(self.nova_policy_file_backup)
        elif self.add_policy_file:
            os.remove(self.nova_policy_file)

        if self.add_policy_file or self.policy_modified:
            os.system('screen -S stack -p n-api -X stuff "^C^M^[[A^M"')
            self.add_policy_file = False
            self.policy_modified = False
