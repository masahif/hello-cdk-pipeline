from aws_cdk import core
from aws_cdk import aws_iam
from aws_cdk import app_delivery
from aws_cdk import aws_codebuild
from aws_cdk import aws_codecommit
from aws_cdk import aws_codepipeline
from aws_cdk import aws_codepipeline_actions
import boto3
import os

class HelloCdkPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, deploy_stack: core.Stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        parameters = get_parameters('/masa/github/')

        # ========================================
        # CodePipeline
        # ========================================
        codepipeline = aws_codepipeline.Pipeline(
            self,
            id='sample_pipeline',
            pipeline_name='sample_pipeline',
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
            project_name='build_project'
        )

        # Add policies to code build role to allow access to the Parameter store.
        project.add_to_role_policy(
            aws_iam.PolicyStatement(
                resources=['*'],
                actions=['ssm:GetParameters']
            )
        )

        # Add build stage to my pipeline.
        build_output = aws_codepipeline.Artifact('build_output')
        codepipeline.add_stage(
            stage_name='Build',
            actions=[
                aws_codepipeline_actions.CodeBuildAction(
                    action_name='CodeBuild',
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
    