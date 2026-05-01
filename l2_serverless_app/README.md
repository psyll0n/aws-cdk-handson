# l2\_serverless\_app — Serverless Application with L2 Constructs

Builds a complete serverless backend using **L2 CDK constructs**, wiring together AWS Lambda, DynamoDB, and CloudWatch monitoring. A public HTTP endpoint is exposed via a Lambda Function URL, making the API accessible without API Gateway.

---

## What You Will Learn

- How to define a DynamoDB table with L2 constructs
- How to define a Python Lambda function and bundle local source code as an asset
- How to pass environment variables from CDK to Lambda
- How to grant least-privilege IAM permissions using `grant_read_data`
- How to expose a Lambda function over HTTP with a Function URL
- How to create a CloudWatch alarm on a Lambda error metric

---

## Architecture

```
HTTP Client
     │  HTTPS
     ▼
┌─────────────────────┐
│  Lambda Function URL │  (unauthenticated)
└──────────┬──────────┘
           │  invoke
           ▼
┌──────────────────────┐        ┌──────────────────────┐
│  ProductListFunction │ ──────►│  ProductsTable        │
│  (Python 3.13)       │  Scan  │  (DynamoDB, on-demand)│
└──────────────────────┘        └──────────────────────┘
           │  errors metric
           ▼
┌──────────────────────────────────────────────┐
│  CloudWatch Alarm                            │
│  triggers if errors ≥ 1 in any 5-min window  │
└──────────────────────────────────────────────┘
```

---

## AWS Resources Created

| Resource | Name / ID | Notes |
|---|---|---|
| DynamoDB Table | `ProductsTable` | Partition key: `id` (String); on-demand billing; `DESTROY` removal policy |
| Lambda Function | `ProductListFunction` | Python 3.13; scans the table and returns all items as JSON |
| Lambda Function URL | — | Unauthenticated (`NONE`) HTTP endpoint; URL emitted as a stack output |
| CloudWatch Alarm | `ProductListFunctionErrorsAlarm` | Triggers on ≥ 1 Lambda error in a 5-minute period |

---

## Project Structure

```
l2_serverless_app/
├── app.py                                      # CDK application entry point
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies (aws-cdk-lib, boto3)
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
├── lambda_src/
│   └── product_list_function.py               # Lambda handler: scans DynamoDB, returns JSON
└── l2_serverless_app/
    ├── __init__.py
    └── l2_serverless_app_stack.py             # Stack definition
```

---

## Lambda Handler

`lambda_src/product_list_function.py` performs a DynamoDB `Scan` and returns all items:

```python
products = dynamodb_client.scan(TableName=os.environ['TABLE_NAME'])
return {"statusCode": 200, "body": json.dumps(products['Items'])}
```

The table name is injected at deploy time via the `TABLE_NAME` environment variable.

---

## Prerequisites

- Python 3.8+
- Node.js (required by the CDK CLI)
- AWS CDK CLI — `npm install -g aws-cdk`
- AWS credentials configured (`aws configure` or environment variables)

---

## Setup & Deployment

```bash
# 1. Navigate into this project
cd l2_serverless_app

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate.bat     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Bootstrap your AWS environment (first time only, per account/region)
cdk bootstrap

# 5. Preview the CloudFormation template
cdk synth

# 6. Deploy to AWS
cdk deploy
# After deploy, the Function URL is printed under "Outputs"

# 7. Test the endpoint
curl <ProductListFunctionURL>

# 8. Tear down all resources when done
cdk destroy
```

---

## Key Concepts

| Concept | Description |
|---|---|
| `dynamodb.Table` | L2 construct — creates table with billing mode, key schema, and removal policy |
| `_lambda.Function` | L2 construct — bundles local code, sets runtime and environment variables |
| `_lambda.Code.from_asset()` | Packages a local directory as a deployment ZIP uploaded to S3 |
| `grant_read_data()` | Attaches a least-privilege IAM policy (read-only) to the Lambda execution role |
| `add_function_url()` | Attaches a public HTTPS URL directly to the Lambda function |
| `metric_errors().create_alarm()` | One-liner CloudWatch alarm on the built-in Lambda errors metric |

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Same app using L3 AWS Solutions Constructs | [`l3_cdk_patterns`](../l3_cdk_patterns/README.md) |
| VPC with L2 constructs | [`l2_cdk_constructs`](../l2_cdk_constructs/README.md) |
