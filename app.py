#!/usr/bin/env python3

from aws_cdk import core

from hello_cdk_pipeline.hello_cdk_pipeline_stack import HelloCdkPipelineStack
from hello_cdk.hello_cdk_stack import HelloCdkStack

app = core.App()
hello_cdk = HelloCdkStack(app, "hello-cdk")
HelloCdkPipelineStack(app, "hello-cdk-pipeline", deploy_stack=hello_cdk)

app.synth()
