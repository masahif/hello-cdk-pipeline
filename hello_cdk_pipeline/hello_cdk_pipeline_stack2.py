from aws_cdk import (core, aws_codebuild as codebuild,
                     aws_codecommit as codecommit,
                     aws_codepipeline as codepipeline,
                     aws_codepipeline_actions as codepipeline_actions,
                     aws_lambda as lambda_)
import boto3
import os

def get_parameters(path):
    ssm = boto3.client('ssm', region_name='ap-northeast-1')
    response = ssm.get_parameters_by_path(
        Path=path,
        WithDecryption=True,
    )

    parameters={}
    for p1 in response['Parameters']:
        parameters[os.path.basename(p1['Name'])] = p1['Value']

    return parameters
    
class HelloCdkPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, repo_name: str=None,
                 lambda_code: lambda_.CfnParametersCode=None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        parameters = get_parameters('/masa/github/')

        source_output = codepipeline.Artifact()
        cdk_build_output = codepipeline.Artifact("CdkBuildOutput")

        owner = 'masahif'
        repo = 'hello-cdk-pipeline'
        branch = 'codebuild'
        oauth_token = parameters['token']

        # Create source collect stage.
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name='source_collect_action_from_github',
            owner=owner,
            repo=repo,
            branch=branch,
            trigger=codepipeline_actions.GitHubTrigger.POLL,
            oauth_token=core.SecretValue.plain_text(oauth_token),
            output=source_output
        )

        cdk_build = codebuild.PipelineProject(self, "CdkBuild",
                        build_spec=codebuild.BuildSpec.from_object(dict(
                            version="0.2",
                            phases=dict(
                                install=dict(
                                    commands=[
                                        "npm install aws-cdk",
                                        "npm update",
                                        "python -m pip install -r requirements.txt"
                                    ]),
                                build=dict(commands=[
                                    "npx cdk synth -o dist"])),
                            artifacts={
                                "base-directory": "dist",
                                "files":'**/*'
                            },
                            environment=dict(buildImage=
                                codebuild.LinuxBuildImage.STANDARD_2_0))))


        codepipeline.Pipeline(self, "Pipeline",
            stages=[
                codepipeline.StageProps(stage_name="Source",
                    actions=[source_action]
                ),
                codepipeline.StageProps(stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="CDK_Build",
                            project=cdk_build,
                            input=source_output,
                            outputs=[cdk_build_output]
                        )
                    ]
                ),
                codepipeline.StageProps(stage_name="Deploy",
                    actions=[
                        codepipeline_actions.CloudFormationCreateUpdateStackAction(
                            action_name="Lambda_CFN_Deploy",
                            template_path=cdk_build_output.at_path(
                                "hello-cdk.template.json"),
                            stack_name="LambdaDeploymentStack",
                            admin_permissions=True,
                        )
                    ]
                ),
            ]
        )