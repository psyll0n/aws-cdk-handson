import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_stack_tagging.cdk_stack_tagging_stack import CdkStackTaggingStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_stack_tagging/cdk_stack_tagging_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkStackTaggingStack(app, "cdk-stack-tagging")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
