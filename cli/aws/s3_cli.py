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
import re

'''
This is S3 Command Class
'''


class S3Cli(AwsCli):

    # constructor.
    def __init__(self):
        super().__init__(None)

    # upload objects into the bucket in S3

    def upload(self, local_dir: str, s3_dir: str, exclude=None, include=None):
        cmd = f"aws s3 cp {local_dir} {s3_dir} --recursive --output yaml "
        if exclude:
            cmd += f"--exclude {re.escape(exclude)} "
        if include:
            cmd += f"--include {re.escape(include)} "
        S3Cli.execCmd(cmd)


    # download objects from the bucket in S3

    def download(self, local_dir: str, s3_dir: str, exclude=None, include=None):
        cmd = f"aws s3 cp {s3_dir} {local_dir} --recursive --output yaml "
        if exclude:
            cmd += f"--exclude {re.escape(exclude)} "
        if include:
            cmd += f"--include {re.escape(include)} "
        S3Cli.execCmd(cmd)


    # remove files on the bucket in S3

    def remove(self, s3_path: str, exclude=None, include=None):
        cmd = f"aws s3 rm {s3_path} --recursive --output yaml "
        if exclude:
            cmd += f"--exclude {re.escape(exclude)} "
        if include:
            cmd += f"--include {re.escape(include)} "
        S3Cli.execCmd(cmd)

    # list files on the bucket in S3

    def ls(self, s3_path=None):
        cmd = f"aws s3 ls --output yaml "
        if s3_path:
            cmd += f"{re.escape(s3_path)} "
        S3Cli.execCmd(cmd)
