# -*- coding: utf-8 -*-
import os
import yaml
from ..cli import Cli

'''
This is AWS Command Class
'''


class AwsCli(Cli):

    ''' constructor.
    Args:
        aws_profile (str): AWS Profile Name (define it in ~/.aws/credentials).
        region (str): the target region.
        environment (str, optional): the target environment.
    '''

    def __init__(self, aws_profile: str, environment=None, region='ap-northeast-1'):
        self.aws_profile = aws_profile
        os.environ['AWS_PROFILE'] = aws_profile
        cmd = f"aws sts get-caller-identity --output yaml"
        output = AwsCli.execCmd(cmd)
        output_yaml = yaml.safe_load(output.stdout)
        self.aws_account = output_yaml['Account']
        self.aws_arn = output_yaml['Arn']
        self.region = region
        if environment is not None:
            self.environment = environment

    ''' destructor
    '''

    def __del__(self):
        if self.environment is not None:
            del self.environment
        del self.region
        del self.aws_arn
        del self.aws_account
        del self.aws_profile

    ''' get information of IAM Roles.
    Returns:
        dict: IAM Roles.
    '''
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
