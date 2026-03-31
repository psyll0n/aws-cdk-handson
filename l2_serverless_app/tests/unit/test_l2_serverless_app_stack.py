import aws_cdk as core
import aws_cdk.assertions as assertions

from l2_serverless_app.l2_serverless_app_stack import L2ServerlessAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in l2_serverless_app/l2_serverless_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = L2ServerlessAppStack(app, "l2-serverless-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
