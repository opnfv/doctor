##############################################################################
# Copyright (c) 2017 NEC Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os
import socket
import getpass
import sys

from monitor.base import BaseMonitor


class CollectdMonitor(BaseMonitor):
    def __init__(self, conf, inspector_url, log):
        super(CollectdMonitor, self).__init__(conf, inspector_url, log)
        self.top_dir = os.path.dirname(sys.path[0])
        tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tmp_sock.connect(("8.8.8.8", 80))

        ## control_ip is the IP of primary interface of control node i.e.
        ## eth0, eno1. It is used by collectd monitor to communicate with
        ## sample inspector.
        ## TODO (umar) see if mgmt IP of control is a better option. Also
        ## primary interface may not be the right option
        self.control_ip = tmp_sock.getsockname()[0]
        self.compute_user = getpass.getuser()
        self.interface_name = os.environ.get('INTERFACE_NAME') or ''
        self.inspector_type = os.environ.get('INSPECTOR_TYPE', 'sample')
        self.auth_url = os.environ.get('OS_AUTH_URL')
        self.username = os.environ.get('OS_USERNAME')
        self.password = os.environ.get('OS_PASSWORD')
        self.project_name = os.environ.get('OS_PROJECT_NAME')
        self.user_domain_name = os.environ.get('OS_USER_DOMAIN_NAME') or 'default'
        self.user_domain_id = os.environ.get('OS_USER_DOMAIN_ID')
        self.project_domain_name = os.environ.get('OS_PROJECT_DOMAIN_NAME') or 'default'
        self.project_domain_id = os.environ.get('OS_PROJECT_DOMAIN_ID')
        self.ssh_opts_cpu = '-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

    def start(self, host):
        self.log.info("Collectd monitor start.........")
        self.compute_host = host.name
        self.compute_ip = host.ip
        f = open("%s/tests/collectd.conf" % self.top_dir, 'w')
        collectd_conf_file = """ 
Hostname %s
FQDNLookup false
Interval 1
MaxReadInterval 2

<LoadPlugin python>
Globals true
</LoadPlugin>
LoadPlugin ovs_events
LoadPlugin logfile

<Plugin logfile>
    File \"/var/log/collectd.log\"
    Timestamp true
    LogLevel \"info\"
</Plugin>

<Plugin python>
    ModulePath \"/home/%s\"
    LogTraces true
    Interactive false
    Import \"collectd_plugin\"
    <Module \"collectd_plugin\">
        control_ip \"%s\"
        compute_ip \"%s\"
        compute_host \"%s\"
        compute_user \"%s\"
        inspector_type \"%s\"
        os_auth_url \"%s\"
        os_username \"%s\"
        os_password \"%s\"
        os_project_name \"%s\"
        os_user_domain_name \"%s\"
        os_user_domain_id \"%s\"
        os_project_domain_name \"%s\"
        os_project_domain_id \"%s\"
    </Module>
</Plugin>

<Plugin ovs_events>
    Port 6640
    Socket \"/var/run/openvswitch/db.sock\"
    Interfaces \"@INTERFACE_NAME@\"
    SendNotification true
    DispatchValues false
</Plugin>
            """ % (self.compute_host, self.compute_user, self.control_ip, self.compute_ip, self.compute_host, self.compute_user,
                   self.inspector_type, self.auth_url, self.username, self.password, self.project_name, self.user_domain_name,
                   self.user_domain_id, self.project_domain_name, self.project_domain_id)
        f.write(collectd_conf_file)
        f.close()

        os.system(" scp %s %s/tests/collectd.conf %s@%s: " % (self.ssh_opts_cpu, self.top_dir, self.compute_user, self.compute_ip))
        self.log.info("after first scp")
        ## @TODO (umar) Always assuming that the interface is assigned an IP if
        ## interface name is not provided. See if there is a better approach
        os.system(""" ssh %s %s@%s \"if [ -n \"%s\" ]; then
            dev=%s
        else
            dev=\$(sudo ip a | awk '/ %s\//{print \$NF}')
        fi
        sed -i -e \"s/@INTERFACE_NAME@/\$dev/\" collectd.conf
        collectd_conf=/opt/collectd/etc/collectd.conf
        if [ -e \$collectd_conf ]; then
            sudo cp \$collectd_conf \${collectd_conf}-doctor-saved
        else
            sudo touch \${collectd_conf}-doctor-created
        fi
        sudo mv collectd.conf /opt/collectd/etc/collectd.conf\" """ % (self.ssh_opts_cpu, self.compute_user, self.compute_ip, self.interface_name, self.interface_name, self.compute_ip))
        self.log.info("after first ssh")
        os.system(" scp  %s %s/tests/lib/monitors/collectd/collectd_plugin.py %s@%s:collectd_plugin.py " % (self.ssh_opts_cpu, self.top_dir, self.compute_user, self.compute_ip))
        self.log.info("after sec scp")
        os.system(" ssh %s %s@%s \"sudo pkill collectd; sudo /opt/collectd/sbin/collectd\" " % (self.ssh_opts_cpu, self.compute_user, self.compute_ip))
        self.log.info("after sec ssh")

    def stop(self):
        os.system(" ssh %s %s@%s \"sudo pkill collectd\" " % (self.ssh_opts_cpu, self.compute_user, self.compute_ip))

    def cleanup(self):
        os.system(""" ssh %s %s@%s \"
            collectd_conf=/opt/collectd/etc/collectd.conf
            if [ -e \"\${collectd_conf}-doctor-created\" ]; then
                sudo rm \"\${collectd_conf}-doctor-created\"
                sudo rm \$collectd_conf
            elif [ -e \"\${collectd_conf}-doctor-saved\" ]; then
                sudo cp -f \"\${collectd_conf}-doctor-saved\" \$collectd_conf
                sudo rm \"\${collectd_conf}-doctor-saved\"
            fi\" """ % (self.ssh_opts_cpu, self.compute_user, self.compute_ip))
        os.remove("%s/tests/collectd.conf" % self.top_dir)
