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
from .aws_cli import AwsCli

'''
This is DynamoDB Command Class
'''
class DynamodbCli(AwsCli):

    # constructor.
    def __init__(self):
        super().__init__(None)


    # create a table.
    def createTable(self, table_name):
        json_data = DynamodbCli.loadJson(f"config/dynamodb/{table_name}.json", DynamodbCli.RETURN_TYPE_STRING)
        cmd = f"aws dynamodb create-table --output text --cli-input-json '{json_data}'"
        DynamodbCli.execCmd(cmd)


    # delete a table.
    def deleteTable(self, table_name):
        cmd = f"aws dynamodb delete-table --table-name {table_name}"
        DynamodbCli.execCmd(cmd)