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
import traceback
import inspect


'''
This is Command Class
'''
class Cli:
    CMD_OPTION_STOP = 1
    CMD_OPTION_CONTINUE = 2
    RETURN_TYPE_DICT = 1
    RETURN_TYPE_STRING = 2

    # constructor.
    def __init__(self):
        pass


    # destructor.
    def __del__(self):
        pass


    # execute a command
    @staticmethod
    def execCmd(cmd :str, error_option=1):
        try:
            print(f' ---------- [COMMAND] {cmd} ---------- ')
            result = subprocess.run(
                cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)
            if result.returncode == 0:
                print(termcolor.colored(result.returncode, 'green'))
                print(termcolor.colored(pprint.pformat(result.stdout), 'green'))
                print(termcolor.colored(pprint.pformat(result.stderr), 'green'))
                print(' ------------------------------ ')
                return result
            else:
                if error_option == Cli.CMD_OPTION_STOP:
                    print(termcolor.colored(result.returncode, 'red'))
                    print(termcolor.colored(pprint.pformat(result.stdout), 'red'))
                    print(termcolor.colored(pprint.pformat(result.stderr), 'red'))
                    raise Exception('ERROR happened. Stop this process.')
                elif error_option == Cli.CMD_OPTION_CONTINUE:
                    print(termcolor.colored(result.returncode, 'yellow'))
                    print(termcolor.colored(pprint.pformat(result.stdout), 'yellow'))
                    print(termcolor.colored(pprint.pformat(result.stderr), 'yellow'))
                    return result
        except Exception as e:
            print(termcolor.colored(f"{e}", 'red'))
            print(termcolor.colored(f"Caller : ", 'red'))
            for stack in inspect.stack():
                print(termcolor.colored(f"{stack.filename},{stack.function},{stack.lineno}", 'red'))
            print(termcolor.colored(f"Stacktrace : {traceback.format_exc()}", 'red'))
            sys.exit()


    # get a random string
    @staticmethod
    def getRandomStr(num):
        return ''.join(random.choices(string.ascii_lowercase + string.digits + '-', k=num))


    # get a current time
    @staticmethod
    def getNow():
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


    # load a file as yaml format
    @staticmethod
    def loadYaml(file_path: str):
        with open(file_path) as file:
            return yaml.safe_load(file)


    # load a file as json format
    @staticmethod
    def loadJson(file_path: str, return_type=1):
        with open(file_path) as file:
            json_data = json.load(file)
            if return_type == Cli.RETURN_TYPE_STRING:
                json_data = json.dumps(json_data, sort_keys=True, indent=2)
            return json_data

