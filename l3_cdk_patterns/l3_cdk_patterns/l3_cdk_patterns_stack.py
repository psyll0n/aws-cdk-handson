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
from aws_solutions_constructs.aws_lambda_dynamodb import LambdaToDynamoDB


# This stack creates a serverless application using AWS Lambda and DynamoDB with the AWS Solutions Constructs pattern.
class L3CdkPatternsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create a Lambda function with a DynamoDB table using the AWS Solutions Constructs pattern
        products_backend = LambdaToDynamoDB(self, "ProductsBackend",
                                          lambda_function_props=_lambda.FunctionProps(
                                              code=_lambda.Code.from_asset("lambda_src"),
                                              handler="product_list_function.lambda_handler",
                                              runtime=_lambda.Runtime.PYTHON_3_13,
                                          ),
                                          table_environment_variable_name="TABLE_NAME",
                                          table_permissions='Read'
                                          )
        
        # Store a reference to the DynamoDB table created by the construct in a variable for later use
        products_table = products_backend.dynamo_table
        
        # Set the DynamoDB table's removal policy to DESTROY so that it will be deleted when the stack is deleted
        products_table.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # Set the products_list_function variable to reference the Lambda function created by the construct for later use
        product_list_function = products_backend.lambda_function
        
        # Add permissions for Scan operation on the DynamoDB table
        # The 'Read' permission only grants basic read operations; we need to explicitly grant Scan permission
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
        
        # Create a CloudWatch alarm based on the Lambda function's error metric
        errors_metric.create_alarm(self, "ProductListFunctionErrorsAlarm",
                                    evaluation_periods=1,
                                    threshold=1,
                                    comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                                    alarm_description="Alarm if the ProductListFunction Lambda function has 1 or more errors in a 5 minute period.",
                                    treat_missing_data=cloudwatch.TreatMissingData.IGNORE
                                    )
