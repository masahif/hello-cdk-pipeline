from aws_cdk import {
    core,
    aws_lambda,
}

class HelloCdkStack(core.Stack):
  def __init__(self, app: core.App, id: str, **kwargs):
    super().__init__(app, id, **kwargs)
      
    func = aws_lambda.Function(self, 
        "Lambda",
        code=aws_lambda.AssetCode(path="./src"),
        handler="hello.handler",
        runtime=lambda_.Runtime.PYTHON_3_8,
    )  
