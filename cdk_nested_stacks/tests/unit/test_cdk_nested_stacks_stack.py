import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_nested_stacks.cdk_nested_stacks_stack import CdkNestedStacksStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_nested_stacks/cdk_nested_stacks_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkNestedStacksStack(app, "cdk-nested-stacks")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
