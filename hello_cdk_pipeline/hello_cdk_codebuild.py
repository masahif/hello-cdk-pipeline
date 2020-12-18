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
