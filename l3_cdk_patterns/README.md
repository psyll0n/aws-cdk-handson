# l3\_cdk\_patterns — Serverless Application with L3 AWS Solutions Constructs

Rebuilds the same serverless application from [`l2_serverless_app`](../l2_serverless_app/README.md) using an **L3 AWS Solutions Constructs pattern** (`LambdaToDynamoDB`). This demonstrates how pre-built, well-architected patterns eliminate boilerplate further and enforce AWS best practices automatically (encryption, logging, IAM least privilege).

---

## What You Will Learn

- What L3 constructs are and how they differ from L1 and L2
- How to use the `aws-solutions-constructs` library
- The `LambdaToDynamoDB` pattern: what it provisions and what defaults it enforces
- How to extend a Solutions Construct (adding extra permissions, function URLs, alarms)
- How to reference resources created inside a pattern (`products_backend.lambda_function`, `.dynamo_table`)

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
┌────────────────────────────────────────────────────┐
│  LambdaToDynamoDB  (Solutions Constructs pattern)  │
│                                                    │
│  ┌──────────────────────┐   ┌────────────────────┐ │
│  │  ProductListFunction │──►│  ProductsTable     │ │
│  │  (Python 3.13)       │   │  (DynamoDB,        │ │
│  └──────────────────────┘   │   on-demand,       │ │
│                             │   encrypted)       │ │
│                             └────────────────────┘ │
└────────────────────────────────────────────────────┘
           │  errors metric
           ▼
┌──────────────────────────────────────────────────────┐
│  CloudWatch Alarm                                    │
│  triggers if errors ≥ 1 in any 5-min window          │
└──────────────────────────────────────────────────────┘
```

---

## AWS Resources Created

| Resource | How created | Notes |
|---|---|---|
| Lambda Function | `LambdaToDynamoDB` pattern | Python 3.13; `TABLE_NAME` env var injected by pattern |
| DynamoDB Table | `LambdaToDynamoDB` pattern | On-demand, encrypted at rest; `DESTROY` removal policy applied post-creation |
| IAM Permissions | Pattern + `grant_read_data()` | Pattern grants base `Read`; explicit `grant_read_data` adds `Scan` |
| Lambda Function URL | `add_function_url()` | Unauthenticated HTTPS endpoint; URL in stack outputs |
| CloudWatch Alarm | `metric_errors().create_alarm()` | ≥ 1 Lambda error in 5-minute window |

---

## Project Structure

```
l3_cdk_patterns/
├── app.py                                      # CDK application entry point
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies (aws-cdk-lib, solutions constructs, boto3)
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
├── lambda_src/
│   └── product_list_function.py               # Lambda handler: scans DynamoDB, returns JSON
└── l3_cdk_patterns/
    ├── __init__.py
    └── l3_cdk_patterns_stack.py               # Stack using LambdaToDynamoDB pattern
```

---

## Lambda Handler

Identical to `l2_serverless_app` — performs a DynamoDB `Scan` and returns all items:

```python
products = dynamodb_client.scan(TableName=os.environ['TABLE_NAME'])
return {"statusCode": 200, "body": json.dumps(products['Items'])}
```

---

## Prerequisites

- Python 3.8+
- Node.js (required by the CDK CLI)
- AWS CDK CLI — `npm install -g aws-cdk`
- AWS credentials configured (`aws configure` or environment variables)

> **Note on dependency pinning:** `aws-cdk-lib` is pinned to `==2.245.0` in `requirements.txt` due to a compatibility constraint with `aws-solutions-constructs` and the CDK Cloud Assembly Schema. Do not upgrade `aws-cdk-lib` without also verifying Solutions Constructs compatibility.

---

## Setup & Deployment

```bash
# 1. Navigate into this project
cd l3_cdk_patterns

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
| L3 constructs | Pre-built, multi-resource patterns from AWS Solutions Constructs |
| `LambdaToDynamoDB` | Provisions Lambda + DynamoDB together, wires env vars, IAM, and encryption |
| `table_permissions='Read'` | Pattern sets base read permissions; `grant_read_data()` adds `Scan` |
| `.lambda_function` / `.dynamo_table` | Escape hatches to access underlying L2 constructs inside the pattern |
| `apply_removal_policy(DESTROY)` | Applied after pattern creation to override the default RETAIN policy |

---

## L2 vs L3 Comparison

```python
# L2 (l2_serverless_app) — explicit resource definitions:
products_table = dynamodb.Table(self, "ProductsTable", ...)
product_list_function = _lambda.Function(self, "ProductListFunction", ...)
products_table.grant_read_data(product_list_function)

# L3 (this project) — pattern does all of the above in one construct:
products_backend = LambdaToDynamoDB(self, "ProductsBackend",
    lambda_function_props=...,
    table_permissions='Read')
```

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Same app using L2 constructs (explicit) | [`l2_serverless_app`](../l2_serverless_app/README.md) |
| VPC with L2 constructs | [`l2_cdk_constructs`](../l2_cdk_constructs/README.md) |
