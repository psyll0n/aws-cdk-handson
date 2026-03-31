import aws_cdk as core
import aws_cdk.assertions as assertions

from l1_cdk_constructs.l1_cdk_constructs_stack import L1CdkConstructsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in l1_cdk_constructs/l1_cdk_constructs_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = L1CdkConstructsStack(app, "l1-cdk-constructs")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
