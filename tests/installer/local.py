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

from installer.base import BaseInstaller
from utils import match_in_file


class LocalInstaller(BaseInstaller):
    computer_user_name = 'root'
    nova_policy_file = '/etc/nova/policy.json'
    nova_policy_file_backup = '%s%s' % (nova_policy_file, '.bak')

    def __init__(self, conf, log):
        super(LocalInstaller, self).__init__(conf, log)
        self.file_modified = False
        self.need_to_rm = False

    def get_computer_user_name(self):
        return self.computer_user_name

    def get_ssh_key_from_installer(self):
        self.log.info('Assuming SSH keys already exchanged with computer for local installer type')
        return

    def setup(self):
        self.get_ssh_key_from_installer()
        self.installer_apply_patches()

    def cleanup(self):
        self.restore_apply_patches()

    def installer_apply_patches(self):
        entry="os_compute_api:servers:show:host_status"
        new="rule:admin_or_owner"
        reg_exp = '%s%s%s' % (entry, '.*', new)

        if os.path.isfile(self.nova_policy_file):
            match = match_in_file(self.nova_policy_file, reg_exp)
            if match:
                self.log.info('Not modifying nova policy')
                return
            else:
                self.file_modified = True
                self.log.info('modify nova policy: servers_show_host_status')
                shutil.copyfile(self.nova_policy_file,
                                self.nova_policy_file_backup)
                rule_prefix = '%s%s%s' % (entry, '.*', 'rule:')
                reg = '%s%s%s' % ('(?<=', rule_prefix, ')\w+')
                match_old = match_in_file(self.nova_policy_file, reg)
                if match_old:
                    # modify the policy
                    with open(self.nova_policy_file, "r+") as file:
                        s = file.read()
                        file.write(s.replace(match_old.group(),
                                             'admin_or_owner'))
                else:
                    # add the policy
                    with open(self.nova_policy_file, "r+") as file:
                        # position before '}'
                        file.seek(-2, os.SEEK_END)
                        file.write('\n    "os_compute_api:servers:show:host_status": "rule:admin_or_owner" \n}')
        else:
            # file does not exit, create a new one and add the policy
            self._add_policy_file_and_context()

        os.system('screen -S stack -p n-api -X stuff "^C^M^[[A^M"')

    def _add_policy_file_and_context(self):
        self.log.info('nova policy file not exist. Creating a new one')

        file_context = [
            '{\n',
            '    "context_is_admin":  "role:admin", \n',
            '    "owner" : "user_id:%(user_id)s", \n',
            '    "admin_or_owner": "rule:context_is_admin or rule:owner", \n',
            '    "os_compute_api:servers:show:host_status": "rule:admin_or_owner" \n',
            '}'
        ]
        with open(self.nova_policy_file, "w") as file:
            file.writelines(file_context)
        self.need_to_rm = True

    def restore_apply_patches(self):
        if self.file_modified:
            shutil.copyfile(self.nova_policy_file_backup, self.nova_policy_file)
            os.remove(self.nova_policy_file_backup)
        elif self.need_to_rm:
            os.remove(self.nova_policy_file)

        if self.need_to_rm or self.file_modified:
            os.system('screen -S stack -p n-api -X stuff "^C^M^[[A^M"')
            self.need_to_rm = False
            self.file_modified = False
