import aws_cdk as core
import aws_cdk.assertions as assertions

from l3_cdk_patterns.l3_cdk_patterns_stack import L3CdkPatternsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in l3_cdk_patterns/l3_cdk_patterns_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = L3CdkPatternsStack(app, "l3-cdk-patterns")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
