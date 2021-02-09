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
from ..cli_enum import CliEnum
import re

'''
This is Lambda Command Class
'''


class LambdaCli(AwsCli):

    # constructor.
    def __init__(self, environment: str):
        super().__init__(environment)

    # create the lambda function

    def createFunction(self, function_name: str, zip_file: str, role: str, timeout: int, memory_size: int, layers: list, description=None):
        cmd = f"aws lambda create-function --function-name {function_name} " \
            '--runtime python3.8 ' \
            f"--role {role} " \
            f'--handler {function_name}.lambda_handler ' \
            f"--timeout {timeout} " \
            f"--memory-size {memory_size} " \
            f"--zip-file fileb://{zip_file} --output yaml "
        if description:
            cmd += f"--description {re.escape(description)} "
        if self._environment:
            syntax = f"Variables={{AWS_LAMBDA_FUNCTION_ALIAS={self._environment}}}"
            cmd += f"--environment {syntax} "
        if layers:
            cmd += f"--layers {' '.join(layers)} "
        LambdaCli.execCmd(cmd)

    # TODO: dynamodb と同様に--cli-input-jsonでupload知るように修正
    # update the lambda function

    def updateFunction(self, function_name: str, zip_file: str, role: str, timeout: int, memory_size: int, layers: list, description=None):
        cmd = f"aws lambda update-function-code --function-name {function_name} --zip-file fileb://{zip_file} --output yaml"
        LambdaCli.execCmd(cmd)
        cmd = f"aws lambda update-function-configuration --function-name {function_name} --output yaml " \
            '--runtime python3.8 ' \
            f"--role {role} " \
            f'--handler {function_name}.lambda_handler ' \
            f"--timeout {timeout} " \
            f"--memory-size {memory_size} "
        if description:
            cmd += f"--description {re.escape(description)} "
        if self._environment:
            syntax = f"Variables={{AWS_LAMBDA_FUNCTION_ALIAS={self._environment}}}"
            cmd += f"--environment {syntax} "
        if layers:
            cmd += f"--layers {' '.join(layers)} "
        LambdaCli.execCmd(cmd)

    # create the lambda alias

    def createAlias(self, funciton_name: str, version: str, description=None):
        cmd = f"aws lambda create-alias --function-name {funciton_name} --name {self._environment} --function-version {re.escape(version)} --output yaml"
        if description:
            cmd += f"--description {re.escape(description)} "
        LambdaCli.execCmd(cmd)

    # update the lambda alias

    def updateAlias(self, funciton_name: str, version: str, description=None):
        cmd = f"aws lambda update-alias --function-name {funciton_name} --name {self._environment} --function-version {re.escape(version)} --output yaml"
        if description:
            cmd += f"--description {re.escape(description)} "
        LambdaCli.execCmd(cmd)

    # add permission into the lambda function which registered to API.

    def addPermission(self, api_id: str, functions: str):
        region = LambdaCli.getRegion()
        account_id = LambdaCli.getAccountid()
        for func in functions:
            statement_id = LambdaCli.getRandomStr(36)
            function_name = f"arn:aws:lambda:{region}:{account_id}:function:{func['lambda_name']}:{self._environment}"
            for method in func['methods']:
                if method == 'OPTIONS':
                    continue
                source_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/{method}/{func['resource_name']}"
                if self.__exsistsPermission(
                        func['lambda_name'], source_arn):
                    continue
                cmd = f"aws lambda add-permission  --function-name '{function_name}'  --source-arn '{source_arn}'  --principal apigateway.amazonaws.com  --statement-id {statement_id}  --action lambda:InvokeFunction  --output yaml"
                LambdaCli.execCmd(cmd)

    # creates a version from the current code and configuration of a function of AWS Lambda.

    def publishFunction(self, function_name: str, description=None):
        cmd = f"aws lambda publish-version --function-name {function_name} --output yaml"
        if description:
            cmd += f" --description {re.escape(description)}"
        output = LambdaCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        return output_yaml['Version']

    # creates an AWS Lambda layer from a ZIP archive.

    def publishLayer(self, layer_name: str, zip_file: str, description=None):
        cmd = f"aws lambda publish-layer-version --layer-name {layer_name} --license-info 'MIT' --compatible-runtimes python3.8 --zip-file fileb://{zip_file} --output yaml"
        if description:
            cmd += f" --description {re.escape(description)}"
        LambdaCli.execCmd(cmd)

    # check whether the lambda function exists or not

    def existsFunction(self, function_name: str):
        cmd = f"aws lambda get-function --function-name {function_name} --output yaml"
        output = LambdaCli.execCmd(cmd, CliEnum.CMD_OPTION_CONTINUE)
        return True if output.returncode == 0 \
            else False

    # check whether the alias of the lambda function exists or not

    def existsAlias(self, function_name: str):
        cmd = f"aws lambda get-alias --function-name {function_name} --name {self._environment} --output yaml"
        output = LambdaCli.execCmd(cmd, CliEnum.CMD_OPTION_CONTINUE)
        return True if output.returncode == 0 \
            else False

    # check whether the permission of the lambda function exists or not

    def __exsistsPermission(self, function_name: str, source_arn: str):
        cmd = f"aws lambda get-policy --function-name '{function_name}:{self._environment}' --output yaml"
        output = LambdaCli.execCmd(cmd, CliEnum.CMD_OPTION_CONTINUE)
        if not output.returncode == 0:
            return False
        output_yaml = yaml.safe_load(output.stdout)
        return True if source_arn in output_yaml['Policy'] \
            else False

    # get layers information.

    def getLayers(self):
        cmd = 'aws lambda list-layers --compatible-runtime python3.8 --output yaml'
        output = LambdaCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        layers = dict()
        for layer in output_yaml['Layers']:
            layers[layer['LayerName']] = {
                'LayerArn': layer['LayerArn'],
                'LayerVersionArn': layer['LatestMatchingVersion']['LayerVersionArn']
            }
        return layers
