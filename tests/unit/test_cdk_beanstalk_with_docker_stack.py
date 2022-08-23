import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_beanstalk_with_docker.cdk_beanstalk_with_docker_stack import CdkBeanstalkWithDockerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_beanstalk_with_docker/cdk_beanstalk_with_docker_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkBeanstalkWithDockerStack(app, "cdk-beanstalk-with-docker")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
