# -*- coding: utf-8 -*-

import subprocess
from subprocess import PIPE
import termcolor
import json
import yaml
import sys
import random
import string
import datetime
import pprint
from pathlib import Path
import os
from dotenv import load_dotenv
from ..cli import Cli 


'''
This is Docker Command Class
'''
class DockerCli(Cli):

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

