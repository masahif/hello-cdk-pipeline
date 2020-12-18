#!/usr/bin/env python3

from aws_cdk import core

#from hello_cdk_pipeline.hello_cdk_pipeline_stack import HelloCdkPipelineStack, HelloCdkCodeBuildStack
from hello_cdk.hello_cdk_stack import HelloCdkStack
from hello_cdk_pipeline.hello_cdk_pipeline_stack import HelloCdkPipelineStack

import os

app = core.App()
hello_cdk = HelloCdkStack(app, "hello-cdk")

#HelloCdkCodeBuildStack(app, "hello-cdk-pipeline", deploy_stack=hello_cdk)

if os.getenv("DEPLOY_PIPELINE"):
    HelloCdkPipelineStack(app, "pipeline-hello-cdk", deploy_stack=hello_cdk)

app.synth()
