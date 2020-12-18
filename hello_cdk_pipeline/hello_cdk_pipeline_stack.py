from aws_cdk import core
from aws_cdk import aws_iam
from aws_cdk import app_delivery
from aws_cdk import aws_codebuild
from aws_cdk import aws_codecommit
from aws_cdk import aws_codepipeline
from aws_cdk import aws_codepipeline_actions
from aws_cdk import aws_s3
import boto3
import os

class HelloCdkCodeBuildStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, deploy_stack: core.Stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        parameters = get_parameters('/masa/github/')

        bucket = aws_s3.Bucket(self,
            'hello-cdk-bucket',
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        artifacts = aws_codebuild.Artifacts.s3(
            bucket=bucket,
            include_build_id=False,
            identifier="AddArtifact1",
            path="artifacts/test",
        )

        github_source = aws_codebuild.Source.git_hub(
            owner='masahif',
            repo='hello-cdk-pipeline',
            branch_or_ref='codebuild',
        )

        with open('buildspec.yml') as f:
            buildspec = f.read()
        
        project = aws_codebuild.Project(
            self,
            'codebuild_project',
            project_name='hello-cdk-codebuild-project',
            build_spec=aws_codebuild.BuildSpec.from_object({
                    "version": "0.2",
                    "phases": {
                        "install": {
                            "runtime-versions": {"python": '3.8"'},
                            "commands": [
                                "python3 -m pip install -e .",
                                "npm install -g aws-cdk@1.76.0",
                            ],
                        },
                        "build": {
                            "commands": [
                                "cdk synth hello-cdk",
                            ]
                        }
                    },
                    "artifacts": {
                        "base-directory": "cdk.out",
                        "files": "**/*"
                    }
                }),
                source=github_source,
                artifacts=artifacts,
        )
        project.add_to_role_policy(
            aws_iam.PolicyStatement(
                resources=['*'],
                actions=['ssm:GetParameter*', "secretsmanager:GetSecretValue", "kms:Decrypt"],
            )
        )
        bucket.grant_read_write(project)

        # codepipeline = aws_codepipeline.Pipeline(
        #     self,
        #     id='hello-cdk-pipeline',
        #     pipeline_name='hello-cdk-pipeline',
        # )

        # source_action = aws_codepipeline_actions.S3SourceAction(
        #     action_name='fetch_source_from_s3',
        #     bucket=bucket,
        #     bucket_key="artifacts/test",
        #     trigger=aws_codepipeline_actions.S3Trigger.POLL,
        # )
        # bucket.grant_read_write(source_action)
        # pipeline.add_stage(
        #     stage_name="source",
        #     actions=[source_action],
        # )

class HelloCdkPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, deploy_stack: core.Stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        parameters = get_parameters('/masa/github/')

        # ========================================
        # CodePipeline
        # ========================================
        codepipeline = aws_codepipeline.Pipeline(
            self,
            id='hello-cdk-pipeline',
            pipeline_name='hello-cdk-pipeline',
        )


        # ============ source stage start ============
        source_output = aws_codepipeline.Artifact('source_output')

        # Change to your setting.
        owner = 'masahif'
        repo = 'hello-cdk-pipeline'
        branch = 'main'
        oauth_token = parameters['token']

        # Create source collect stage.
        source_action = aws_codepipeline_actions.GitHubSourceAction(
            action_name='source_collect_action_from_github',
            owner=owner,
            repo=repo,
            branch=branch,
            trigger=aws_codepipeline_actions.GitHubTrigger.POLL,
            oauth_token=core.SecretValue.plain_text(oauth_token),
            output=source_output
        )
        # Add source stage to my pipeline.
        codepipeline.add_stage(
            stage_name='Source',
            actions=[source_action]
        )
        # ============ source stage end ==============


        # ============ build stage start =============
        # Create build project.
        project = aws_codebuild.PipelineProject(
            self,
            id='build_project',
            project_name='hello-cdk-build-project'
        )

        # Add policies to code build role to allow access to the Parameter store.
        project.add_to_role_policy(
            aws_iam.PolicyStatement(
                resources=['*'],
                actions=['ssm:GetParameter*', "secretsmanager:GetSecretValue", "kms:Decrypt"],
            )
        )

        # Add build stage to my pipeline.
        build_output = aws_codepipeline.Artifact('build_output')
        codepipeline.add_stage(
            stage_name='hello-cdk-build-stage',
            actions=[
                aws_codepipeline_actions.CodeBuildAction(
                    action_name='hello-cdk-build-action',
                    project=project,
                    input=source_output,
                    outputs=[build_output]
                )
           ]
        )
        # ============ build stage end ===============

        # ============ deploy stage start ============
        # Add deploy stage to pipeline.
        codepipeline.add_stage(
            stage_name='Deploy',
            actions=[
                app_delivery.PipelineDeployStackAction(
                    stack=deploy_stack,
                    input=build_output,
                    admin_permissions=True,
                    change_set_name='sample-change-set'
                )
            ]
        )
        # ============ deploy stage end ==============


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
    