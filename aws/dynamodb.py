# -*- coding: utf-8 -*-
from .aws import Aws
from ..cli_enum import CliEnum

'''
This is DynamoDB Command Class
'''


class Dynamodb(Aws):

    ''' constructor.
        Refer super class's constructor.
    '''

    def __init__(self, aws_profile: str, environment=None, region='ap-northeast-1'):
        super().__init__(aws_profile=aws_profile, environment=environment, region=region)

    # create a table.

    def createTable(self, table_name: str):
        json_data = Dynamodb.loadJson(
            f"config/dynamodb/{table_name}.json", CliEnum.RETURN_TYPE_STRING)
        cmd = f"aws dynamodb create-table --output text --cli-input-json '{json_data}'"
        Dynamodb.execCmd(cmd)

    # delete a table.

    def deleteTable(self, table_name: str):
        cmd = f"aws dynamodb delete-table --table-name {table_name}"
        Dynamodb.execCmd(cmd)
