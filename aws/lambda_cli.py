# -*- coding: utf-8 -*-
# the following is not necessary if Python version is 3.9 or over.
from __future__ import annotations

import yaml
import re
from .aws_cli import AwsCli
from ..cli_enum import CliEnum

'''
This is Lambda Command Class
'''


class LambdaCli(AwsCli):

    ''' constructor.
        Refer super class's constructor.
    '''

    def __init__(self, aws_profile: str, environment: str, region='ap-northeast-1') -> LambdaCli:
        super().__init__(aws_profile=aws_profile, environment=environment, region=region)

    ''' create the lambda function.
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/create-function.html
    Args:
        function_name (str): The name of the Lambda function.
        zip_file (str): The path to the zip file of the code you are uploading.
        role (str): The function’s execution IAM role.
        timeout (int): The amount of time that Lambda allows a function to run before stopping it. 
        memory_size (int): The amount of memory available to the function at runtime.
        layers (str): A list of function layers to add to the function’s execution environment. 
        description (str, optional): the description of this function.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''

    def createFunction(self, function_name: str, zip_file: str, role: str, timeout: int, memory_size: int, layers: list, description=None) -> subprocess.CompletedProcess:
        cmd = f"aws lambda create-function --function-name {function_name} " \
            '--runtime python3.8 ' \
            f"--role {role} " \
            f'--handler {function_name}.lambda_handler ' \
            f"--timeout {timeout} " \
            f"--memory-size {memory_size} " \
            f"--zip-file fileb://{zip_file} --output yaml "
        if description:
            cmd += f"--description {re.escape(description)} "
        if self.environment:
            syntax = f"Variables={{AWS_LAMBDA_FUNCTION_ALIAS={self.environment}}}"
            cmd += f"--environment {syntax} "
        if layers:
            cmd += f"--layers {' '.join(layers)} "
        LambdaCli.execCmd(cmd)

    ''' update the lambda function.
        TODO: dynamodb と同様に--cli-input-jsonでupload知るように修正
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/update-function-code.html
    Args:
        function_name (str): The name of the Lambda function.
        zip_file (str): The path to the zip file of the code you are uploading.
        role (str): The function’s execution IAM role.
        timeout (int): The amount of time that Lambda allows a function to run before stopping it. 
        memory_size (int): The amount of memory available to the function at runtime.
        layers (str): A list of function layers to add to the function’s execution environment. 
        description (str, optional): the description of this function.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''
    def updateFunction(self, function_name: str, zip_file: str, role: str, timeout: int, memory_size: int, layers: list, description=None) -> subprocess.CompletedProcess:
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
        if self.environment:
            syntax = f"Variables={{AWS_LAMBDA_FUNCTION_ALIAS={self.environment}}}"
            cmd += f"--environment {syntax} "
        if layers:
            cmd += f"--layers {' '.join(layers)} "
        LambdaCli.execCmd(cmd)

    ''' create the lambda alias
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/create-alias.html
    Args:
        function_name (str): The name of the Lambda function.
        version (str): The function version that the alias invokes.
        description (str, optional): A description of the alias.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''
    def createAlias(self, funciton_name: str, version: str, description=None) -> subprocess.CompletedProcess:
        cmd = f"aws lambda create-alias --function-name {funciton_name} --name {self.environment} --function-version {re.escape(version)} --output yaml"
        if description:
            cmd += f"--description {re.escape(description)} "
        LambdaCli.execCmd(cmd)

    ''' update the lambda alias
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/update-alias.html
    Args:
        function_name (str): The name of the Lambda function.
        version (str): The function version that the alias invokes.
        description (str, optional): A description of the alias.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''
    def updateAlias(self, funciton_name: str, version: str, description=None) -> subprocess.CompletedProcess:
        cmd = f"aws lambda update-alias --function-name {funciton_name} --name {self.environment} --function-version {re.escape(version)} --output yaml"
        if description:
            cmd += f"--description {re.escape(description)} "
        LambdaCli.execCmd(cmd)

    ''' add permission into the lambda function in order to registere API Gateway.
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/add-permission.html
    Args:
        api_id (str): API ID of on the API Gateway.
        functions (str): A list of function names.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''
    def addPermission(self, api_id: str, functions: str) -> subprocess.CompletedProcess:
        for func in functions:
            statement_id = LambdaCli.getRandomStr(36)
            function_name = f"arn:aws:lambda:{self.region}:{self.aws_account}:function:{func['lambda_name']}:{self.environment}"
            for method in func['methods']:
                if method == 'OPTIONS':
                    continue
                source_arn = f"arn:aws:execute-api:{self.region}:{self.aws_account}:{api_id}/*/{method}/{func['resource_name']}"
                if self.__exsistsPermission(
                        func['lambda_name'], source_arn):
                    continue
                cmd = f"aws lambda add-permission  --function-name '{function_name}'  --source-arn '{source_arn}'  --principal apigateway.amazonaws.com  --statement-id {statement_id}  --action lambda:InvokeFunction  --output yaml"
                LambdaCli.execCmd(cmd)

    ''' create a version from the current code and configuration of a function of AWS Lambda.
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/publish-version.html
    Args:
        function_name (str): The name of the Lambda function.
        description (str, optional): A description of the alias.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''
    def publishFunction(self, function_name: str, description=None) -> subprocess.CompletedProcess:
        cmd = f"aws lambda publish-version --function-name {function_name} --output yaml"
        if description:
            cmd += f" --description {re.escape(description)}"
        output = LambdaCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        return output_yaml['Version']

    ''' creates an AWS Lambda layer from a ZIP archive.
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/publish-layer-version.html
    Args:
        function_name (str): The name of the Lambda function.
        zip_file (str): The path to the zip file of the code you are uploading.
        description (str, optional): A description of the alias.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''
    def publishLayer(self, layer_name: str, zip_file: str, description=None) -> subprocess.CompletedProcess:
        cmd = f"aws lambda publish-layer-version --layer-name {layer_name} --license-info 'MIT' --compatible-runtimes python3.8 --zip-file fileb://{zip_file} --output yaml"
        if description:
            cmd += f" --description {re.escape(description)}"
        LambdaCli.execCmd(cmd)

    ''' check whether the lambda function exists or not.
    Args:
        function_name (str): The name of the Lambda function.
    Returns:
        bool: whether the lambda function exists or not.
    '''
    def existsFunction(self, function_name: str) -> bool:
        cmd = f"aws lambda get-function --function-name {function_name} --output yaml"
        output = LambdaCli.execCmd(cmd, CliEnum.CMD_OPTION_CONTINUE)
        return True if output.returncode == 0 \
            else False

    ''' check whether the alias of the lambda function exists or not.
    Args:
        function_name (str): The name of the Lambda function.
    Returns:
        bool: whether the alias of the lambda function exists or not.
    '''
    def existsAlias(self, function_name: str) -> bool:
        cmd = f"aws lambda get-alias --function-name {function_name} --name {self.environment} --output yaml"
        output = LambdaCli.execCmd(cmd, CliEnum.CMD_OPTION_CONTINUE)
        return True if output.returncode == 0 \
            else False

    ''' check whether the permission of the lambda function exists or not.
    Args:
        function_name (str): The name of the Lambda function.
        source_arn (str): source arn of lambda function.
    Returns:
        bool: whether the permission of the lambda function exists or not.
    '''
    def __exsistsPermission(self, function_name: str, source_arn: str) -> bool:
        cmd = f"aws lambda get-policy --function-name '{function_name}:{self.environment}' --output yaml"
        output = LambdaCli.execCmd(cmd, CliEnum.CMD_OPTION_CONTINUE)
        if not output.returncode == 0:
            return False
        output_yaml = yaml.safe_load(output.stdout)
        return True if source_arn in output_yaml['Policy'] \
            else False

    ''' get layers information.
    Returns:
        dict: layers information.
    '''
    def getLayers(self) -> dict:
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
