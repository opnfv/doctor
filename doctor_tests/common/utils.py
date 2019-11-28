##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import json
import os
import paramiko
import re
import subprocess


def load_json_file(full_path):
    """Loads JSON from file
    :param target_filename:
    :return:
    """
    if not os.path.isfile(full_path):
        raise Exception('File(%s) does not exist' % full_path)

    with open(full_path, 'r') as file:
        return json.load(file)


def write_json_file(full_path, data):
    """write JSON from file
    :param target_filename:
    :return:
    """

    with open(full_path, 'w+') as file:
        file.write(json.dumps(data))


def match_rep_in_file(regex, full_path):
    if not os.path.isfile(full_path):
        raise Exception('File(%s) does not exist' % full_path)

    with open(full_path, 'r') as file:
        for line in file:
            result = re.search(regex, line)
            if result:
                return result

    return None


def get_doctor_test_root_dir():
    current_dir = os.path.split(os.path.realpath(__file__))[0]
    return os.path.dirname(current_dir)


class SSHClient(object):
    def __init__(self, ip, username, password=None, pkey=None,
                 key_filename=None, log=None, look_for_keys=False,
                 allow_agent=False):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.client.connect(ip, username=username, password=password,
                            pkey=pkey, key_filename=key_filename,
                            look_for_keys=look_for_keys,
                            allow_agent=allow_agent)
        self.log = log

    def __del__(self):
        self.client.close()

    def ssh(self, command, raise_enabled=True):
        if self.log:
            self.log.info("Executing: %s" % command)
        stdin, stdout, stderr = self.client.exec_command(command)
        ret = stdout.channel.recv_exit_status()
        output = list()
        for line in stdout.read().splitlines():
            output.append(line.decode('utf-8'))
        if ret and raise_enabled:
            if self.log:
                self.log.info("*** FAILED to run command %s (%s)"
                              % (command, ret))
            raise Exception(
                "Unable to run \ncommand: %s\nret: %s"
                % (command, ret))
        if self.log:
            self.log.info("*** SUCCESSFULLY run command %s" % command)
        return ret, output

    def scp(self, source, dest, method='put'):
        if self.log:
            self.log.info("Copy %s -> %s" % (source, dest))
        ftp = self.client.open_sftp()
        if method == 'put':
            ftp.put(source, dest)
        elif method == 'get':
            ftp.get(source, dest)
        ftp.close()


class LocalSSH(object):

    def __init__(self, log):
        self.log = log
        self.log.info('Init local ssh client')

    def ssh(self, cmd):
        ret = 0
        output = "%s failed!!!" % cmd
        try:
            output = subprocess.check_output((cmd), shell=True,
                                             universal_newlines=True)
        except subprocess.CalledProcessError:
            ret = 1
        return ret, output

    def scp(self, src_file, dst_file):
        return subprocess.check_output("cp %s %s" % (src_file, dst_file),
                                       shell=True)


def run_async(func):
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return async_func
