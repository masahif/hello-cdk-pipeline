from aws_cdk import (
    core,
    aws_codebuild,
)

class HelloCdkCodebuildStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        github_source = aws_codebuild.Source.git_hub(
            owner='masahif',
            repo='hello-cdk-pipeline',
            branch_or_ref='codebuild',
        )

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
                }),
                source=github_source,
        )
