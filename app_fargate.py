#!/usr/bin/env python3

import os
import argparse
from aws_cdk import core
from modules.stack.fargate_stack import FargateStack
from modules.dataload.config import Config


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--stack-name', required=True)
parser.add_argument('-d', '--deploy-config', required=True)
parser.add_argument('-o', '--overrides', nargs='*', default=[])
args = parser.parse_args()

app = core.App()
config = Config(
    deploy_config=args.deploy_config,
    overrides=args.overrides
)
FargateStack(
    scope=app,
    id='fargate',
    config=config,
    stack_name=args.stack_name,
    env={'region': os.environ['AWS_DEFAULT_REGION']}
)

app.synth()
