import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="cdkpipeline_lambda",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "hello_cdk_pipeline"},
    packages=setuptools.find_packages(where="cdkpipeline_lambda"),

    install_requires=[
        "boto3",
        "aws-cdk.core==1.76.0",
        "aws_cdk.aws_iam==1.76.0",
        "aws_cdk.aws_codepipeline_actions==1.76.0",
        "aws_cdk.aws_codepipeline==1.76.0",
        "aws_cdk.aws_codebuild==1.76.0",
        "aws_cdk.app_delivery==1.76.0",
    ],

    python_requires=">=3.7",

    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
