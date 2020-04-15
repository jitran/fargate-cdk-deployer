#!/bin/bash -e

cd /cdk
source .env/bin/activate
cdk "$@"
