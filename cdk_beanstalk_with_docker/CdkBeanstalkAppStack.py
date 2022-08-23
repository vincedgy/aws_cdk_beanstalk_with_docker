import os

import boto3
from aws_cdk import (
    aws_elasticbeanstalk as elastic_beanstalk,
    Stack, NestedStack, CfnOutput, aws_iam as iam,
    aws_s3_assets as aws_s3_assets
)
from constructs import Construct


class BeanstalkEnvStack(Stack):

    def createEnvironment(self, application_name, environment_name, solution_stack_name):
        # get the latest beanstalk application version

        app_name = f"{application_name}-{environment_name}"

        client = boto3.client('elasticbeanstalk')

        application_versions = client.describe_application_versions(
            ApplicationName=application_name
        )

        version_label = None

        if (len(application_versions['ApplicationVersions']) > 0):
            version_label = application_versions['ApplicationVersions'][0]['VersionLabel']

        beanstalk_env_config_template = elastic_beanstalk.CfnConfigurationTemplate(
            self,
            "Elastic-Beanstalk-Env-Config",
            application_name=application_name,
            solution_stack_name=solution_stack_name,
            option_settings=[
                elastic_beanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty(
                    namespace="aws:autoscaling:asg", option_name="MinSize", value="2"
                ),

                elastic_beanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty(
                    namespace="aws:autoscaling:asg", option_name="MaxSize", value="4"
                )
            ]

        )

        # configure an instance profile
        my_role = iam.Role(self, "Elastic-Beanstalk-Environment-Role",
                           assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        managed_policy = iam.ManagedPolicy.from_aws_managed_policy_name('AWSElasticBeanstalkWebTier')
        my_role.add_managed_policy(managed_policy)
        instance_profile_name = f"{app_name}-Profile"
        iam.CfnInstanceProfile(self, instance_profile_name,
                                                  instance_profile_name=instance_profile_name,
                                                  roles=[my_role.role_name])

        # configure the environment for auto-scaling
        beanstalk_env = elastic_beanstalk.CfnEnvironment(
            self,
            "Elastic-Beanstalk-Environment",
            application_name=application_name,
            environment_name=environment_name,
            solution_stack_name=solution_stack_name,
            version_label=version_label,

            option_settings=[
                elastic_beanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration", option_name="IamInstanceProfile",
                    value=instance_profile_name
                ),
                elastic_beanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:asg", option_name="MinSize", value="2"
                ),
                elastic_beanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:asg", option_name="MaxSize", value="4"
                ),
                elastic_beanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace='aws:ec2:instances',
                    option_name='InstanceTypes',
                    value='t2.micro',
                ),

            ]
        )

    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.createEnvironment(props['application_name'], props['environment_name'], props['solution_stack_name'])


class BeanstalkAppStack(Stack):

    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        def createApplication(application_name):
            elastic_beanstalk.CfnApplication(
                self,
                "Elastic-Beanstalk",
                application_name=application_name,
                description="AWS Elastic Beanstalk Demo",
            )

        createApplication(props['application_name'])

        BeanstalkAppVersionStack(self, "BeanstalkAppVersionStack", props, **kwargs)


class BeanstalkAppVersionStack(NestedStack):
    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        app_version = elastic_beanstalk.CfnApplicationVersion(
            self,
            "application_version",
            application_name=props['application_name'],
            source_bundle=elastic_beanstalk.CfnApplicationVersion.SourceBundleProperty(
                s3_bucket=props['s3bucket_name'],
                s3_key=props['s3bucket_obj_key']
            ),

        )


class BeanstalkS3Stack(Stack):
    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # the asset is uploaded to the cdktoolkit-stagingbucket

        s3_bucket_asset = aws_s3_assets.Asset(
            self,
            "s3-asset",
            path=os.path.abspath(props['s3_asset'])
        )

        # debugging print s3 object url to console output
        output = CfnOutput(
            self,
            "S3_object_url",
            value=s3_bucket_asset.s3_object_url,
            description="S3 object url"
        )

        output = CfnOutput(
            self,
            "S3_object_key",
            value=s3_bucket_asset.s3_object_key,
            description="S3 object key"
        )

        output = CfnOutput(
            self,
            "S3_bucket_name",
            value=s3_bucket_asset.s3_bucket_name,
            description="S3 bucket name"
        )

        self.output_props = props.copy()
        self.output_props['s3bucket_name'] = s3_bucket_asset.s3_bucket_name
        self.output_props['s3bucket_obj_key'] = s3_bucket_asset.s3_object_key

    # pass objects to another stack

    @property
    def outputs(self):
        return self.output_props
