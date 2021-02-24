# -*- coding: utf-8 -*-
from .aws_cli import AwsCli
import re

'''
This is S3 Command Class
'''


class S3Cli(AwsCli):

    ''' constructor.
        Refer super class's constructor.
    '''

    def __init__(self, aws_profile: str, environment=None, region='ap-northeast-1'):
        super().__init__(aws_profile=aws_profile, environment=environment, region=region)

    ''' upload objects into the bucket in S3
    Args:
        local_dir (str): Local directry path which has target objects to upload.
        bucket_name (str): Target S3 bucket name.
        prefix_name (str): Target prefix name on the target backet.
        exclude (str, optional): exclude objects with UNIX style wildcards.
        include (str, optional): include objects with UNIX style wildcards.
    e.g.
        from cli.aws.s3 import S3
        s3_cli = S3('default')
        s3_cli.upload('./data', 'MY_BUCKET', 'MY_FOLDER/MY_SUB_FOLDER', "*", "*.txt")
        --> it will upload only files ending with .txt:
    '''

    def upload(self, local_dir: str, bucket_name: str, prefix_name: str, exclude=None, include=None):
        cmd = f"aws s3 cp {local_dir} s3://{bucket_name}/{prefix_name} --recursive --output yaml "
        if exclude:
            cmd += f"--exclude {re.escape(exclude)} "
        if include:
            cmd += f"--include {re.escape(include)} "
        S3.execCmd(cmd)

    ''' download objects into the bucket in S3
    Args:
        local_dir (str): Local directry path in which the target objects will be download.
        bucket_name (str): Target S3 bucket name.
        prefix_name (str): Target prefix name on the target backet.
        exclude (str, optional): exclude objects with UNIX style wildcards.
        include (str, optional): include objects with UNIX style wildcards.
    e.g.
        from cli.aws.s3 import S3
        s3_cli = S3('default')
        s3_cli.download('~/Downloads/', 'MY_BUCKET', 'MY_FOLDER/MY_SUB_FOLDER')
    '''

    def download(self, local_dir: str, bucket_name: str, prefix_name: str, exclude=None, include=None):
        cmd = f"aws s3 cp s3://{bucket_name}/{prefix_name} {local_dir} --recursive --output yaml "
        if exclude:
            cmd += f"--exclude {re.escape(exclude)} "
        if include:
            cmd += f"--include {re.escape(include)} "
        S3.execCmd(cmd)

    ''' remove objects on the bucket in S3
    Args:
        bucket_name (str): Target S3 bucket name.
        prefix_name (str): Target prefix name on the target backet.
        exclude (str, optional): exclude objects with UNIX style wildcards.
        include (str, optional): include objects with UNIX style wildcards.
    '''

    def remove(self, s3_path: str, exclude=None, include=None):
        cmd = f"aws s3 rm s3://{bucket_name}/{prefix_name} --recursive --output yaml "
        if exclude:
            cmd += f"--exclude {re.escape(exclude)} "
        if include:
            cmd += f"--include {re.escape(include)} "
        S3.execCmd(cmd)

    ''' list objects on the bucket in S3
    Args:
        bucket_name (str, optional): Target S3 bucket name.
        prefix_name (str, optional): Target prefix name on the target backet.
    '''

    def ls(self, bucket_name=None, prefix_name=None):
        cmd = f"aws s3 ls --recursive --output yaml "
        if bucket_name:
            cmd += f"{re.escape(bucket_name)}/"
            if prefix_name:
                cmd += f"{re.escape(prefix_name)}"
        S3.execCmd(cmd)
