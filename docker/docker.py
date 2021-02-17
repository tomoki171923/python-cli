# -*- coding: utf-8 -*-

import os
from ..cli import Cli


'''
This is Docker Command Class
'''


class Docker(Cli):

    # constructor.
    def __init__(self):
        pass

    # destructor.

    def __del__(self):
        pass

    # check whether the docker process is running or not

    @classmethod
    def isRunning(cls):
        cmd = 'docker ps'
        result = DockerCli.execCmd(cmd)
        result_list = result.stdout.splitlines()
        is_running = False
        if len(result_list) > 1:
            for idx in range(1, len(result_list)):
                image = result_list[idx].split()[1]
                if image == 'amazon/dynamodb-local':
                    is_running = True
                    break
        return is_running
