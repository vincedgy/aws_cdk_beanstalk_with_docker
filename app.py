#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_beanstalk_with_docker.CdkBeanstalkAppStack import BeanstalkEnvStack, BeanstalkAppStack, BeanstalkS3Stack

app = cdk.App()

# a dictionary to store properties
props = {
    'namespace': 'ElasticBeanstalk',
    'application_name': 'GettingStartedApp2',
    'environment_name': 'GettingStartedEnv2',
    'solution_stack_name': '64bit Amazon Linux 2 v3.4.18 running Docker',
    's3_asset': 'assets'
}

s3_bucket = BeanstalkS3Stack(
    app, f"{props['namespace']}-s3",
    props
)

beanstalk_app = BeanstalkAppStack(
    app, f"{props['namespace']}-app",
    s3_bucket.outputs
)

# the beanstalk app stack has a dependency on the creation of a S3 bucket
beanstalk_app.add_dependency(s3_bucket)

beanstalk_env = BeanstalkEnvStack(
    app, f"{props['namespace']}-env",
    props,
)

# the beanstalk environment stack has a dependency on the creation of a beanstalk app
beanstalk_env.add_dependency(beanstalk_app)

app.synth()
