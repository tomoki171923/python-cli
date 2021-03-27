# -*- coding: utf-8 -*-
# the following is not necessary if Python version is 3.9 or over.
from __future__ import annotations

import yaml
from .aws_cli import AwsCli
from typing import List, Tuple, Optional

'''
This is API Gateway Command Class
'''


class ApigatewayCli(AwsCli):

    ''' constructor.
        Refer super class's constructor.
    '''

    def __init__(self, aws_profile: str, environment: str, region='ap-northeast-1') -> ApigatewayCli:
        super().__init__(aws_profile=aws_profile, environment=environment, region=region)

    ''' create API on API Gateway
    Args:
        api_name (str): The name of the API.
    Returns:
        str: API ID.
    '''

    def create(self, api_name: str) -> str:
        api_id, parent_id = self.__createRestapi(api_name)
        resource_id = self.__createResource(api_id, parent_id, "mock")
        self.__putMethod(api_id, resource_id, "GET", "None")
        self.__putIntegration(api_id, resource_id, "GET", "MOCK")
        self.createStage(api_id)
        self.exportApi(api_name, api_id)
        return api_id

    ''' update API on API Gateway
    Args:
        api_name (str): The name of the API.
        api_id (str): The string identifier of the associated RestApi .
        development_id (str): The identifier for the deployment resource.
    '''

    def update(self, api_name: str, api_id: str, development_id: str) -> None:
        self.__importApi(api_id, api_name)
        self.createStage(api_id)
        self.exportApi(api_name, api_id)

    ''' export Rest API
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/apigateway/get-export.html
    Args:
        api_name (str): The name of the API.
        api_id (str): The string identifier of the associated RestApi .
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''

    def exportApi(self, api_name: str, api_id: str) -> subprocess.CompletedProcess:
        cmd = f"aws apigateway get-export --parameters extensions='apigateway' --rest-api-id {api_id} --stage-name {self.environment} --export-type oas30 --accepts application/yaml config/apigateway/{api_name}-{self.environment}-oas30-apigateway.yaml"
        ApigatewayCli.execCmd(cmd)

    ''' check whether the api exists or not
    Args:
        api_name (str): The name of the API.
    Returns:
        tuple: The string identifier of the associated RestApi or None & The identifier for the deployment resource or None.
    '''

    def exsistsApi(self, api_name: str) -> Tuple[Optional[str], Optional[str]]:
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

    ''' deploy api at the stage (create)
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/apigateway/create-deployment.html
    Args:
        api_id (str): The string identifier of the associated RestApi .
    Returns:
        str: The identifier for the deployment resource.
    '''

    def createStage(self, api_id: str) -> str:
        cmd = f"aws apigateway create-deployment --rest-api-id {api_id} --stage-name {self.environment} --variables alias={self.environment} --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        deployment_id = output_yaml["id"]
        return deployment_id

    ''' get lambda infomation from resources
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/apigateway/get-resources.html
    Args:
        api_id (str): The string identifier of the associated RestApi .
    Returns:
        list: lambda info
    '''

    def getLambdaInfos(self, api_id: str) -> List[dict]:
        cmd = f"aws apigateway get-resources --rest-api-id {api_id} --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        lambda_infos = list()
        for item in output_yaml['items']:
            if 'pathPart' in item:
                lambda_name = item['pathPart'].replace("-", "_")
                lambda_info = {'lambda_name': lambda_name,
                               'resource_name': item['pathPart'],
                               'methods': item['resourceMethods']
                               }
                lambda_infos.append(lambda_info)
        return lambda_infos

    ''' create Rest API;
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/apigateway/create-rest-api.html
    Args:
        api_name (str): The name of the API.
    Returns:
        tuple: Specifies a put integration request’s resource ID & The parent resource’s identifier.
    '''

    def __createRestapi(self, api_name: str) -> Tuple[str, str]:
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

    ''' create a resource on the Rest API
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/apigateway/create-resource.html
    Args:
        api_id (str): The string identifier of the associated RestApi .
        parent_id (str): The parent resource’s identifier.
        path_part (str): The last path segment for this resource.
    Returns:
        str: Specifies a put integration request’s resource ID.
    '''

    def __createResource(self, api_id: str, parent_id: str, path_part: str) -> str:
        cmd = f"aws apigateway create-resource --rest-api-id {api_id} --parent-id {parent_id} --path-part {path_part} --output yaml"
        output = ApigatewayCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        resource_id = output_yaml["id"]
        return resource_id

    ''' create a method on the resource
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/apigateway/put-method.html
    Args:
        api_id (str): The string identifier of the associated RestApi .
        resource_id (str): Specifies a put integration request’s resource ID.
        http_method (str): Specifies a put integration request’s HTTP method.
        authorization_type (str): The method’s authorization type. Valid values are NONE for open access, 
            AWS_IAM for using AWS IAM permissions, CUSTOM for using a custom authorizer, 
            or COGNITO_USER_POOLS for using a Cognito user pool.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''

    def __putMethod(self, api_id: str, resource_id: str, http_method: str, authorization_type: str) -> subprocess.CompletedProcess:
        cmd = f"aws apigateway put-method --rest-api-id {api_id} --resource-id {resource_id} --http-method {http_method} --authorization-type {authorization_type}"
        ApigatewayCli.execCmd(cmd)

    ''' set integration into the method
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/apigateway/put-integration.html
    Args:
        api_id (str): The string identifier of the associated RestApi .
        resource_id (str): Specifies a put integration request’s resource ID.
        http_method (str): Specifies a put integration request’s HTTP method.
        type (str): Specifies a put integration input’s type.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''

    def __putIntegration(self, api_id: str, resource_id: str, http_method: str, type: str) -> subprocess.CompletedProcess:
        cmd = f"aws apigateway put-integration --rest-api-id {api_id} --resource-id {resource_id} --http-method {http_method} --type {type}"
        ApigatewayCli.execCmd(cmd)

    ''' import Rest API
        Ref: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/apigateway/put-rest-api.html
    Args:
        api_id (str): The string identifier of the associated RestApi .
        api_name (str): The name of the API.
    Returns:
        subprocess.CompletedProcess: the result of executing command.
    '''

    def __importApi(self, api_id: str, api_name: str) -> subprocess.CompletedProcess:
        cmd = f"aws apigateway put-rest-api --rest-api-id {api_id} --mode overwrite --cli-binary-format raw-in-base64-out --body 'file://config/apigateway/{api_name}-{self.environment}-oas30-apigateway.yaml' --output yaml"
        ApigatewayCli.execCmd(cmd)
