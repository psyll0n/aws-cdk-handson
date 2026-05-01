# starter\_cdk\_app — Basic CDK Starter

A minimal AWS CDK application written in Python that demonstrates the standard project scaffold and basic AWS messaging resources. This is the entry point for the repository — start here if you are new to the AWS CDK.

---

## What You Will Learn

- The anatomy of a CDK Python project (`app.py`, stack file, `cdk.json`)
- How to define AWS resources using CDK constructs
- How to wire two constructs together (SNS → SQS subscription)
- The CDK workflow: `synth` → `bootstrap` → `deploy` → `destroy`

---

## Architecture

```
┌──────────────────────────────────────┐
│  StarterCdkAppStack                  │
│                                      │
│  ┌───────────────┐    subscribes     │
│  │   SNS Topic   │ ────────────────► │
│  └───────────────┘                   │
│                        ┌───────────┐ │
│                        │ SQS Queue │ │
│                        │ (300 s    │ │
│                        │ visibility│ │
│                        │ timeout)  │ │
│                        └───────────┘ │
└──────────────────────────────────────┘
```

---

## AWS Resources Created

| Resource | Name / ID | Notes |
|---|---|---|
| SQS Queue | `StarterCdkAppQueue` | Visibility timeout: 300 seconds |
| SNS Topic | `StarterCdkAppTopic` | Subscribed to the SQS queue above |

---

## Project Structure

```
starter_cdk_app/
├── app.py                                      # CDK application entry point
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
└── starter_cdk_app/
    ├── __init__.py
    └── starter_cdk_app_stack.py                # Stack: SNS topic + SQS queue
```

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
cd starter_cdk_app

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

# 7. Tear down all resources when done
cdk destroy
```

---

## Key Concepts

| Concept | Description |
|---|---|
| `Stack` | A deployable unit of CloudFormation resources |
| `sqs.Queue` | L2 construct that creates an SQS queue with sensible defaults |
| `sns.Topic` | L2 construct that creates an SNS topic |
| `SqsSubscription` | Wires an SNS topic to deliver messages into an SQS queue |

---

## Related Projects

← Back to the [repository root](../README.md)

| Next step | Project |
|---|---|
| VPC with raw CloudFormation resources | [`l1_cdk_constructs`](../l1_cdk_constructs/README.md) |
| VPC with high-level constructs | [`l2_cdk_constructs`](../l2_cdk_constructs/README.md) |
