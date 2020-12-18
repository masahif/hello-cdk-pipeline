#!/usr/bin/env python3

import os
from aws_cdk import core
from hello_cdk.hello_cdk_stack import HelloCdkStack
from cdk_stack.hello_cdk_codebuild_stack import HelloCdkCodebuildStack

app = core.App()
hello_cdk = HelloCdkStack(app, "hello-cdk")

if os.getenv("DEPLOY_PIPELINE"):
    HelloCdkCodebuildStack(app, "codebuild-hello-cdk")

app.synth()
