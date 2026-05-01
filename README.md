# AWS CDK Hands-On

A progressive collection of AWS Cloud Development Kit (CDK) projects written in **Python**, designed to take you from a blank CDK app all the way through advanced architectural patterns. Each subdirectory is a **self-contained, deployable CDK application** that explores a specific concept.

---

## Learning Path

The projects are ordered by increasing complexity. Follow the path below for a structured learning experience, or jump directly to the topic you need.

```
Foundations
  └─► starter_cdk_app       Basic CDK scaffold, SNS + SQS
  └─► l1_cdk_constructs     VPC built from raw CloudFormation (L1) constructs
  └─► l2_cdk_constructs     Same VPC in 4 lines using L2 constructs

Serverless
  └─► l2_serverless_app     Lambda + DynamoDB + CloudWatch alarm (L2)
  └─► l3_cdk_patterns       Same app using L3 AWS Solutions Constructs pattern

Networking & Compute
  └─► cdk_networking        VPC + EC2 (NGINX) + RDS PostgreSQL
  └─► cdk_s3_assets         Static file deployment to EC2 via CDK S3 assets

Multi-Stack Patterns
  └─► cdk_multi_stacks      Two independent stacks with cross-stack VPC reference
  └─► cdk_nested_stacks     Same architecture using CDK NestedStack
  └─► cdk-stack-tagging     Stack & resource tagging (priority, include/exclude, remove)
  └─► cdk-aspects           Custom CDK Aspects for synthesis-time compliance & governance
```

---

## Projects

| # | Directory | Description | AWS Services |
|---|---|---|---|
| 1 | [**starter\_cdk\_app**](starter_cdk_app/README.md) | Minimal CDK app — standard scaffold, SNS topic, SQS queue | SNS, SQS |
| 2 | [**l1\_cdk\_constructs**](l1_cdk_constructs/README.md) | VPC with 4 subnets, IGW, and route tables using raw `CfnXxx` constructs | VPC, EC2 |
| 3 | [**l2\_cdk\_constructs**](l2_cdk_constructs/README.md) | Same VPC topology expressed in 4 lines with the `ec2.Vpc` L2 construct | VPC, EC2 |
| 4 | [**l2\_serverless\_app**](l2_serverless_app/README.md) | Serverless backend: Lambda + DynamoDB + Function URL + CloudWatch alarm (L2) | Lambda, DynamoDB, CloudWatch |
| 5 | [**l3\_cdk\_patterns**](l3_cdk_patterns/README.md) | Same serverless app via `LambdaToDynamoDB` AWS Solutions Constructs pattern (L3) | Lambda, DynamoDB, CloudWatch |
| 6 | [**cdk\_networking**](cdk_networking/README.md) | Full networking stack: VPC, EC2 + NGINX, Elastic IP, RDS PostgreSQL | VPC, EC2, RDS |
| 7 | [**cdk\_s3\_assets**](cdk_s3_assets/README.md) | Deploy a local HTML file to EC2 via CDK S3 assets and user data | VPC, EC2, S3 |
| 8 | [**cdk\_multi\_stacks**](cdk_multi_stacks/README.md) | Split infrastructure into two independent stacks sharing a VPC (cross-stack ref) | VPC, EC2, S3 |
| 9 | [**cdk\_nested\_stacks**](cdk_nested_stacks/README.md) | Same two-stack architecture using `NestedStack` inside one root stack | VPC, EC2, S3 |
| 10 | [**cdk-stack-tagging**](cdk-stack-tagging/README.md) | Apply, prioritise, include/exclude, and remove AWS tags at stack and resource level | VPC, EC2, S3 |
| 11 | [**cdk-aspects**](cdk-aspects/README.md) | Custom `IAspect` that enforces EC2 instance types, emits warnings, and auto-corrects at synthesis time | VPC, EC2, S3 |

---

## Repository Structure

```
aws-cdk-handson/
├── starter_cdk_app/        #  1 — Basic CDK app with SNS and SQS
├── l1_cdk_constructs/      #  2 — VPC networking with L1 (CloudFormation) constructs
├── l2_cdk_constructs/      #  3 — VPC networking with L2 (higher-level) constructs
├── l2_serverless_app/      #  4 — Serverless app using L2 constructs (Lambda + DynamoDB)
├── l3_cdk_patterns/        #  5 — Serverless app using L3 AWS Solutions Constructs
├── cdk_networking/         #  6 — Full networking stack: VPC, EC2, RDS PostgreSQL
├── cdk_s3_assets/          #  7 — Deploying static files to EC2 via S3 assets
├── cdk_multi_stacks/       #  8 — Infrastructure split across multiple CDK stacks
├── cdk_nested_stacks/      #  9 — Infrastructure using CDK nested stacks
├── cdk-stack-tagging/      # 10 — Stack and resource tagging patterns
└── cdk-aspects/            # 11 — Custom CDK Aspects for compliance & governance
```

---

## Common Project Layout

Every project follows the standard CDK Python project structure:

```
<project>/
├── app.py                          # CDK application entry point
├── cdk.json                        # CDK toolkit configuration
├── requirements.txt                # Runtime dependencies (aws-cdk-lib, constructs, …)
├── requirements-dev.txt            # Development dependencies (pytest, aws-cdk assertions)
├── source.bat                      # Windows helper to activate the virtual environment
├── <module>/
│   ├── __init__.py
│   └── <stack_name>_stack.py       # Main CDK stack definition(s)
├── lambda_src/                     # (where applicable) Lambda function source code
├── web_pages/                      # (where applicable) Static web content
└── tests/
    └── unit/
        └── test_<stack>_stack.py   # Unit tests using aws-cdk assertions
```

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.8+ | [python.org](https://www.python.org/downloads/) |
| Node.js | LTS | [nodejs.org](https://nodejs.org/) — required by the CDK CLI |
| AWS CDK CLI | latest | `npm install -g aws-cdk` |
| AWS CLI | v2 | [docs.aws.amazon.com](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) |
| AWS credentials | — | `aws configure` or environment variables |

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/<your-org>/aws-cdk-handson.git
cd aws-cdk-handson

# 2. Navigate into any project
cd starter_cdk_app           # or any other subdirectory

# 3. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate    # Linux / macOS
# .venv\Scripts\activate.bat # Windows

# 4. Install project dependencies
pip install -r requirements.txt

# 5. Bootstrap your AWS environment (once per account/region)
cdk bootstrap

# 6. Synthesize the CloudFormation template
cdk synth

# 7. Deploy to AWS
cdk deploy

# 8. Destroy all resources when done
cdk destroy
```

Each project's own README contains detailed setup, architecture diagrams, resource tables, and key concept explanations.

---

## CDK Construct Levels at a Glance

| Level | Type | Description | Example in this repo |
|---|---|---|---|
| **L1** | `Cfn*` constructs | Direct 1-to-1 CloudFormation resource wrappers | [`l1_cdk_constructs`](l1_cdk_constructs/README.md) |
| **L2** | Standard constructs | Higher-level abstractions with sensible defaults | [`l2_cdk_constructs`](l2_cdk_constructs/README.md), [`l2_serverless_app`](l2_serverless_app/README.md) |
| **L3** | Patterns / Solutions Constructs | Multi-resource, opinionated, well-architected patterns | [`l3_cdk_patterns`](l3_cdk_patterns/README.md) |

---

## License

This repository is provided for educational purposes. See [LICENSE](LICENSE) if present, or treat all content as MIT-licensed.
