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


class SSHClient(object):
    def __init__(self, ip, username, password=None, pkey=None,
                 key_filename=None, log=None, look_for_keys=False,
                 allow_agent=False):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(ip, username=username, password=password,
                            pkey=pkey, key_filename=key_filename,
                            look_for_keys=look_for_keys,
                            allow_agent=allow_agent)
        self.log = log

    def __del__(self):
        self.client.close()

    def ssh(self, command):
        if self.log:
            self.log.debug("Executing: %s" % command)
        stdin, stdout, stderr = self.client.exec_command(command)
        ret = stdout.channel.recv_exit_status()
        output = list()
        for line in stdout.read().splitlines():
            output.append(line.decode('utf-8'))
        if ret:
            if self.log:
                self.log.debug("*** FAILED to run command %s (%s)" % (command, ret))
            raise Exception(
                "Unable to run \ncommand: %s\nret: %s"
                % (command, ret))
        if self.log:
            self.log.debug("*** SUCCESSFULLY run command %s" % command)
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

def run_async(func):
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return async_func
