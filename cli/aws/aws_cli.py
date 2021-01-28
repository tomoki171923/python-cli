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
import boto3
import botocore
import os
from dotenv import load_dotenv
from ..cli import Cli 


'''
This is AWS Command Class
'''
class AwsCli(Cli):
    _account_id = None
    _region = None

    # constructor.
    def __init__(self, environment: str):
        if AwsCli._account_id is None or AwsCli._region is None:
            AwsCli.setProperties()
        self.setEvironment(environment)


    # destructor.
    def __del__(self):
        del self._environment


    def setEvironment(self, environment: str):
        self._environment = environment


    @classmethod
    def setProperties(cls):
        load_dotenv()
        cls._account_id = os.environ['AWS_ACCOUNT_ID']
        cls._region = os.environ['AWS_REGION']


    @classmethod
    def getAccountid(cls):
        return cls._account_id
        

    @classmethod
    def getRegion(cls):
        return cls._region


    # get information of IAM Roles.
    @staticmethod
    def getRoles():
        cmd = 'aws iam list-roles --output yaml'
        output = AwsCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        roles = dict()
        for role in output_yaml['Roles']:
            roles[role['RoleName']] = {
                'Arn': role['Arn'],
                'RoleId': role['RoleId']
            }
        return roles



