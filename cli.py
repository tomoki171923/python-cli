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
from .cli_enum import CliEnum


'''
This is Command Class
'''


class Cli:
    ENUM = CliEnum
    # constructor.

    def __init__(self):
        pass

    # destructor.

    def __del__(self):
        pass

    ''' execute a command.
    Args:
        cmd (str): the command executing.
        error_option (int, optional): the option when an error happens.
            CMD_OPTION_STOP(defalt): stop the processing.  
            CMD_OPTION_CONTINUE: continue the processing.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''
    @staticmethod
    def execCmd(cmd: str, error_option=CliEnum.CMD_OPTION_STOP):
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
                if error_option == CliEnum.CMD_OPTION_STOP:
                    print(termcolor.colored(result.returncode, 'red'))
                    print(termcolor.colored(pprint.pformat(result.stdout), 'red'))
                    print(termcolor.colored(pprint.pformat(result.stderr), 'red'))
                    raise Exception('ERROR happened. Stop this process.')
                elif error_option == CliEnum.CMD_OPTION_CONTINUE:
                    print(termcolor.colored(result.returncode, 'yellow'))
                    print(termcolor.colored(
                        pprint.pformat(result.stdout), 'yellow'))
                    print(termcolor.colored(
                        pprint.pformat(result.stderr), 'yellow'))
                    return result
        except Exception as e:
            print(termcolor.colored(f"{e}", 'red'))
            print(termcolor.colored(f"Caller : ", 'red'))
            for stack in inspect.stack():
                print(termcolor.colored(
                    f"{stack.filename},{stack.function},{stack.lineno}", 'red'))
            print(termcolor.colored(
                f"Stacktrace : {traceback.format_exc()}", 'red'))
            sys.exit()

    ''' get a random string.
    Args:
        count (int): the string count.
    Returns:
        str: the random string.
    '''
    @staticmethod
    def getRandomStr(count: int):
        return ''.join(random.choices(string.ascii_lowercase + string.digits + '-', k=count))

    ''' Get the current time with string.
    Returns:
        str: the current time 
    '''
    @staticmethod
    def now():
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    ''' Loading a file as yaml format
    Args:
        file_path (str): target file path.
    Returns:
        dict: file data
    '''
    @staticmethod
    def loadYaml(file_path: str):
        with open(file_path) as file:
            return yaml.safe_load(file)

    ''' Loading a file as json format
    Args:
        file_path (str): target file path.
        return_type (int, optional): the type of return object
            RETURN_TYPE_DICT(defalt): dict  
            RETURN_TYPE_STRING: str
    Returns:
        dict or str: file data
    '''
    @staticmethod
    def loadJson(file_path: str, return_type=CliEnum.RETURN_TYPE_DICT):
        with open(file_path) as file:
            json_data = json.load(file)
            if return_type == CliEnum.RETURN_TYPE_STRING:
                json_data = json.dumps(json_data, sort_keys=True, indent=2)
            return json_data

    ''' Output standard output message
    Args:
        message (str): the message.
        severity (int, optional): the severity of message.
            SEVERIY_INFO(defalt): level info
            SEVERIY_ERROR: level error
            SEVERIY_WARN: level waring
    '''
    @staticmethod
    def stdout(message: str, severity=CliEnum.SEVERIY_INFO):
        color = 'green'
        if severity == CliEnum.SEVERIY_ERROR:
            color = 'red'
        elif severity == CliEnum.SEVERIY_WARN:
            color = 'yellow'
        print(termcolor.colored(
            f"************ {Cli.now()} : {message} ************", color))
