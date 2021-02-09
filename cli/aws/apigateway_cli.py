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
This is API Gateway Command Class
'''


class ApigatewayCli(AwsCli):

    # constructor.
    def __init__(self, aws_profile: str, region='ap-northeast-1', environment: str)
    super().__init__(aws_profile, region, environment)

    # create API

    def create(self, api_name: str):
        api_id, parent_id = self.__createRestapi(api_name)
        resource_id = self.__createResource(api_id, parent_id, "mock")
        self.__putMethod(api_id, resource_id, "GET", "None")
        self.__putIntegration(api_id, resource_id, "GET", "MOCK")
        self.createStage(api_id)
        self.exportApi(api_id, api_name)
        return api_id

    # update API

    def update(self, api_name: str, api_id: str, development_id: str):
        self.__importApi(api_id, api_name)
        self.createStage(api_id)
        self.exportApi(api_id, api_name)

    # export Rest API

    def exportApi(self, api_id: str, api_name: str):
        cmd = f"aws apigateway get-export --parameters extensions='apigateway' --rest-api-id {api_id} --stage-name {self.environment} --export-type oas30 --accepts application/yaml config/apigateway/{api_name}-{self.environment}-oas30-apigateway.yaml"
        ApigatewayCli.execCmd(cmd)

    # check whether the api exists or not

    def exsistsApi(self, api_name: str):
        api_id = None
        development_id = None
        cmd = f"aws apigateway get-rest-apis --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        for item in output_yaml['items']:
            if item['name'] == api_name:
                api_id = item['id']
                break
        if api_id is not None:
            cmd = f"aws apigateway get-stages --rest-api-id {api_id} --output yaml"
            output = ApigatewayCli.execCmd(cmd)
            output_yaml = yaml.safe_load(output.stdout)
            for item in output_yaml['item']:
                if item['stageName'] == self.environment:
                    development_id = item['deploymentId']
        return api_id, development_id

    # deploy api at the stage (create)

    def createStage(self, api_id: str):
        cmd = f"aws apigateway create-deployment --rest-api-id {api_id} --stage-name {self.environment} --variables alias={self.environment} --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        deployment_id = output_yaml["id"]
        return deployment_id

    # get lambda names from resources

    def getLambdaInfos(self, api_id: str):
        cmd = f"aws apigateway get-resources --rest-api-id {api_id} --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        lambda_names = list()
        for item in output_yaml['items']:
            if 'pathPart' in item:
                lambda_name = item['pathPart'].replace("-", "_")
                lambda_info = {'lambda_name': lambda_name,
                               'resource_name': item['pathPart'],
                               'methods': item['resourceMethods']
                               }
                lambda_names.append(lambda_info)
        return lambda_names

    # create Rest API;

    def __createRestapi(self, api_name: str):
        cmd = f"aws apigateway create-rest-api --name {api_name} --region {self.region} --endpoint-configuration types=REGIONAL --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        # get rest-api-id
        output_yaml = yaml.safe_load(output.stdout)
        rest_api_id = output_yaml['id']
        # get resource-id
        cmd = f"aws apigateway get-resources --rest-api-id {rest_api_id} --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        for item in output_yaml['items']:
            parent_id = item['id']
            break
        return rest_api_id, parent_id

    # create a resource on the Rest API

    def __createResource(self, api_id: str, parent_id: str, path_part: str):
        cmd = f"aws apigateway create-resource --rest-api-id {api_id} --parent-id {parent_id} --path-part {path_part} --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        resource_id = output_yaml["id"]
        return resource_id

    # create a method on the resource

    def __putMethod(self, api_id: str, resource_id: str, http_method: str, authorization_type: str):
        cmd = f"aws apigateway put-method --rest-api-id {api_id} --resource-id {resource_id} --http-method {http_method} --authorization-type {authorization_type}"
        ApigatewayCli.execCmd(cmd)

    # set integration into the method

    def __putIntegration(self, api_id: str, resource_id: str, http_method: str, type: str):
        cmd = f"aws apigateway put-integration --rest-api-id {api_id} --resource-id {resource_id} --http-method {http_method} --type {type}"
        ApigatewayCli.execCmd(cmd)

    # import Rest API

    def __importApi(self, api_id: str, api_name: str):
        cmd = f"aws apigateway put-rest-api --rest-api-id {api_id} --mode overwrite --cli-binary-format raw-in-base64-out --body 'file://config/apigateway/{api_name}-{self.environment}-oas30-apigateway.yaml' --output yaml"
        ApigatewayCli.execCmd(cmd)
