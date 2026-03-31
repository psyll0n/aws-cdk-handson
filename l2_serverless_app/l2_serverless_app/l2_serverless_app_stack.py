from aws_cdk import (
    RemovalPolicy,
    Stack,
    Duration,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    CfnOutput,
    aws_cloudwatch as cloudwatch
)
from constructs import Construct

class L2ServerlessAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        products_table = dynamodb.Table(
            self, "ProductsTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        product_list_function = _lambda.Function(self, "ProductListFunction",
                                                 code=_lambda.Code.from_asset("lambda_src"),
                                                 handler="product_list_function.lambda_handler",
                                                 runtime=_lambda.Runtime.PYTHON_3_13,
                                                 environment={
                                                     "TABLE_NAME": products_table.table_name
                                                 })
        
        # Grant the Lambda function read access to the DynamoDB table
        products_table.grant_read_data(product_list_function)

        # Adding a lambda URL to the lambda function to enable execution via HTTP requests
        product_list_url = product_list_function.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
            )
        
        # Output the Lambda function URL to the CloudFormation stack outputs
        CfnOutput(self, "ProductListFunctionURL", value=product_list_url.url)
        
        # Create a CloudWatch metric for the Lambda function's error metric
        errors_metric = product_list_function.metric_errors(
            label="ProductListFunctionErrors",
            period=Duration.minutes(5),
            statistic=cloudwatch.Stats.SUM
        )
        
        errors_metric.create_alarm(self, "ProductListFunctionErrorsAlarm",
                                    evaluation_periods=1,
                                    threshold=1,
                                    comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                                    alarm_description="Alarm if the ProductListFunction Lambda function has 1 or more errors in a 5 minute period.",
                                    treat_missing_data=cloudwatch.TreatMissingData.IGNORE
                                    )
