# AWS CDK Handson

A collection of hands-on AWS Cloud Development Kit (CDK) projects written in Python, progressing from basic concepts to advanced patterns. Each directory is a self-contained CDK application that demonstrates a specific feature or architectural pattern.

---

## Repository Structure

```
aws-cdk-handson/
├── starter_cdk_app/       # Basic CDK app with SNS and SQS
├── l1_cdk_constructs/     # VPC networking with L1 (CloudFormation) constructs
├── l2_cdk_constructs/     # VPC networking with L2 (higher-level) constructs
├── l2_serverless_app/     # Serverless app using L2 constructs (Lambda + DynamoDB)
├── l3_cdk_patterns/       # Serverless app using L3 AWS Solutions Constructs pattern
├── cdk_networking/        # Full networking setup: VPC, EC2, RDS PostgreSQL
├── cdk_s3_assets/         # Deploying static files to EC2 via S3 assets
├── cdk_multi_stacks/      # Splitting infrastructure across multiple CDK stacks
└── cdk_nested_stacks/     # Infrastructure using CDK nested stacks
```

---

## Projects

### `starter_cdk_app` — Basic CDK Starter

A minimal CDK application that demonstrates the standard project scaffold and basic AWS messaging resources.

**Resources created:**
- An **SQS Queue** with a 300-second visibility timeout.
- An **SNS Topic** subscribed to the SQS queue.

**Key files:**
| File | Description |
|---|---|
| `app.py` | CDK app entry point |
| `starter_cdk_app/starter_cdk_app_stack.py` | Stack definition with SNS topic and SQS queue |

---

### `l1_cdk_constructs` — VPC with L1 (CloudFormation) Constructs

Demonstrates the use of **L1 (Layer 1) CDK constructs**, which are direct mappings to raw CloudFormation resource types (prefixed with `Cfn`). Every networking resource is explicitly defined, giving full control over configuration.

**Resources created:**
- A **VPC** (`10.0.0.0/16`) with DNS support and hostnames enabled.
- An **Internet Gateway** attached to the VPC.
- **4 subnets** across 2 availability zones:
  - `10.0.0.0/24` — Public subnet (AZ 1)
  - `10.0.1.0/24` — Public subnet (AZ 2)
  - `10.0.2.0/24` — Private subnet (AZ 1)
  - `10.0.3.0/24` — Private subnet (AZ 2)
- **Route tables** per subnet, with public subnets routed through the Internet Gateway.

**Key files:**
| File | Description |
|---|---|
| `app.py` | CDK app entry point |
| `l1_cdk_constructs/l1_cdk_constructs_stack.py` | Stack using raw `CfnVPC`, `CfnSubnet`, `CfnRouteTable`, etc. |

---

### `l2_cdk_constructs` — VPC with L2 (Higher-Level) Constructs

Contrasts with the L1 example by using **L2 CDK constructs**, which provide opinionated, higher-level abstractions with sensible defaults. Creating an equivalent VPC requires far fewer lines of code.

**Resources created:**
- A **VPC** spanning up to 3 availability zones, with no NAT gateways (`nat_gateways=0`).

**Key files:**
| File | Description |
|---|---|
| `app.py` | CDK app entry point |
| `l2_cdk_constructs/l2_cdk_constructs_stack.py` | Stack using the L2 `ec2.Vpc` construct |

---

### `l2_serverless_app` — Serverless Application with L2 Constructs

Builds a serverless backend using L2 constructs, wiring together Lambda, DynamoDB, and CloudWatch monitoring.

**Resources created:**
- A **DynamoDB table** (`ProductsTable`) with a string partition key `id`, on-demand billing, and a destroy removal policy.
- A **Lambda function** (`ProductListFunction`) running Python 3.13 that scans the DynamoDB table and returns all items as JSON.
- A **Lambda Function URL** (unauthenticated) that exposes the function over HTTP.
- A **CloudWatch alarm** that triggers if the Lambda function reports 1 or more errors in any 5-minute window.

**Key files:**
| File | Description |
|---|---|
| `app.py` | CDK app entry point |
| `l2_serverless_app/l2_serverless_app_stack.py` | Stack defining DynamoDB, Lambda, Function URL, and CloudWatch alarm |
| `lambda_src/product_list_function.py` | Lambda handler: scans DynamoDB and returns all products |

---

### `l3_cdk_patterns` — Serverless Application with L3 AWS Solutions Constructs

Rebuilds the same serverless application from `l2_serverless_app` using an **L3 AWS Solutions Constructs pattern** (`LambdaToDynamoDB`). This demonstrates how pre-built, well-architected patterns reduce boilerplate further and enforce best practices automatically.

**Resources created:**
- A **Lambda function** + **DynamoDB table** provisioned together via the `LambdaToDynamoDB` Solutions Construct pattern.
- Additional `grant_read_data` permission on the table to allow `Scan` operations (beyond the base `Read` permission set in the pattern).
- A **Lambda Function URL** (unauthenticated) for HTTP access.
- A **CloudWatch alarm** for Lambda errors over a 5-minute period.

**Key files:**
| File | Description |
|---|---|
| `app.py` | CDK app entry point |
| `l3_cdk_patterns/l3_cdk_patterns_stack.py` | Stack using the `LambdaToDynamoDB` Solutions Constructs pattern |
| `lambda_src/product_list_function.py` | Lambda handler: scans DynamoDB and returns all products (same as l2_serverless_app) |

---

### `cdk_networking` — Full Networking Stack (VPC + EC2 + RDS)

A single-stack application demonstrating a realistic networking topology with a public web server and a privately isolated database.

**Resources created:**
- A **VPC** with no NAT gateways (public and private isolated subnets auto-configured by CDK).
- An **EC2 t3.micro instance** running Amazon Linux 2023, placed in the public subnet.
  - **NGINX** installed and started via EC2 user data (`dnf install nginx`).
  - An **Elastic IP** attached for a stable public address.
  - Security group rules allowing inbound **HTTP (port 80)** and **SSH (port 22)** from anywhere.
- An **RDS PostgreSQL 16** instance (`t3.micro`, 20 GB) deployed in a private isolated subnet.
  - Connectivity from the EC2 web server to RDS on **port 5432** is explicitly allowed.
  - MySQL client also installed on the EC2 instance via user data.
- **CloudFormation Outputs**: EC2 public IP, EC2 public DNS, and RDS endpoint address.

**Key files:**
| File | Description |
|---|---|
| `app.py` | CDK app entry point |
| `cdk_networking/cdk_networking_stack.py` | Single stack with VPC, EC2 (NGINX), Elastic IP, RDS PostgreSQL, and security groups |

---

### `cdk_s3_assets` — Deploying Static Files via S3 Assets

Demonstrates how to use **CDK S3 assets** to upload local files during deployment and have them automatically downloaded onto an EC2 instance at boot time via user data.

**Resources created:**
- A **VPC** with no NAT gateways.
- An **EC2 t3.micro instance** (Amazon Linux 2023) in the public subnet running **NGINX**.
- An **Elastic IP** for the instance.
- The local file `web_pages/index.html` is bundled as an **S3 asset**, uploaded to S3 by CDK, and downloaded to `/usr/share/nginx/html/index.html` on the instance via a signed S3 download command in user data.
- The EC2 instance IAM role is automatically granted read access to the S3 asset bucket.

**Key files:**
| File | Description |
|---|---|
| `app.py` | CDK app entry point |
| `cdk_s3_assets/cdk_s3_assets_stack.py` | Stack demonstrating `s3_assets.Asset` and `add_s3_download_command` |
| `web_pages/index.html` | Simple HTML page ("Welcome to My Website!") served by NGINX |

---

### `cdk_multi_stacks` — Multiple CDK Stacks with Cross-Stack References

Demonstrates how to split a CDK application into **multiple independent CloudFormation stacks** that share resources via cross-stack references. The VPC is exported from the `NetworkStack` and consumed by the `ApplicationStack`.

**Stacks:**

#### `NetworkStack` (`network_stack.py`)
- Creates a **VPC** with no NAT gateways and exposes it as `self.vpc` for use by other stacks.

#### `ApplicationStack` (`application_stack.py`)
- Accepts the `main_vpc` reference from `NetworkStack`.
- Deploys an **EC2 t3.micro instance** (Amazon Linux 2023) running **NGINX** in the public subnet.
- Attaches an **Elastic IP** to the instance.
- Downloads the `web_pages/index.html` file from the `cdk_s3_assets` project via an **S3 asset** and serves it from NGINX.
- Opens inbound **HTTP (80)** and **SSH (22)** access.
- Outputs the instance's public IP and DNS name.

**Key files:**
| File | Description |
|---|---|
| `app.py` | Entry point; instantiates `NetworkStack` then passes `network_stack.vpc` to `ApplicationStack` |
| `cdk_multi_stacks/network_stack.py` | Defines the VPC and exposes it for cross-stack use |
| `cdk_multi_stacks/application_stack.py` | Deploys EC2/NGINX using the shared VPC; serves HTML via S3 asset |
| `web_pages/index.html` | HTML page served by the web server |

---

### `cdk_nested_stacks` — CDK Nested Stacks

Mirrors the `cdk_multi_stacks` architecture but uses **CDK `NestedStack`** instead of independent top-level stacks. Both `NetworkStack` and `ApplicationStack` are nested inside a single parent `RootStack`, which results in a single CloudFormation root stack containing nested stack resources.

**Stacks:**

#### `NetworkStack` (`network_stack.py`)
- Extends `NestedStack` (instead of `Stack`).
- Creates a **VPC** with no NAT gateways and exposes it as `self.vpc`.

#### `ApplicationStack` (`application_stack.py`)
- Extends `NestedStack`.
- Same resources as the multi-stacks `ApplicationStack`: EC2 t3.micro with NGINX, Elastic IP, S3 asset HTML page, HTTP/SSH security group rules, and CloudFormation outputs.

**Key files:**
| File | Description |
|---|---|
| `app.py` | Entry point; creates a `RootStack`, then nests `NetworkStack` and `ApplicationStack` inside it |
| `cdk_nested_stacks/network_stack.py` | `NestedStack` defining the shared VPC |
| `cdk_nested_stacks/application_stack.py` | `NestedStack` deploying EC2/NGINX using the VPC from the sibling nested stack |

---

## Common Project Layout

Every project follows the standard CDK Python project structure:

```
<project>/
├── app.py                          # CDK application entry point
├── cdk.json                        # CDK toolkit configuration
├── requirements.txt                # Runtime dependencies (aws-cdk-lib, constructs, etc.)
├── requirements-dev.txt            # Development/test dependencies (pytest, aws-cdk assertions)
├── source.bat                      # Windows helper to activate the virtual environment
├── <project_module>/
│   ├── __init__.py
│   └── <stack_name>_stack.py       # Main CDK stack definition(s)
├── lambda_src/                     # (where applicable) Lambda function source code
├── web_pages/                      # (where applicable) Static web content
└── tests/
    └── unit/
        └── test_<stack>_stack.py   # Unit tests using aws-cdk assertions
```

## Prerequisites

- Python 3.8+
- Node.js (required by the CDK CLI)
- AWS CDK CLI: `npm install -g aws-cdk`
- AWS credentials configured (`aws configure` or environment variables)

## Getting Started

```bash
# Navigate into any project directory
cd starter_cdk_app

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate.bat     # Windows

# Install dependencies
pip install -r requirements.txt

# Bootstrap your AWS environment (first time only)
cdk bootstrap

# Synthesize the CloudFormation template
cdk synth

# Deploy to AWS
cdk deploy

# Destroy the deployed resources
cdk destroy
```
