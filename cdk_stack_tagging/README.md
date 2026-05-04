# cdk\_stack\_tagging — CDK Stack & Resource Tagging

Builds on the [`cdk_multi_stacks`](../cdk_multi_stacks/README.md) architecture to demonstrate all the ways CDK can apply, override, prioritise, and remove **AWS resource tags** — both at the stack level and at the individual resource level.

---

## What You Will Learn

- How `cdk.Tags.of(scope).add()` propagates tags to every resource in a scope
- How **tag priority** (`priority=`) controls which tag wins when multiple rules match the same resource
- How to **include** or **exclude** specific resource types from a tag rule
- How to **remove** a tag from a specific resource using `Tags.of(scope).remove()`
- How stack-level tags interact with resource-level tags

---

## Architecture

```
app.py
 ├── NetworkStack     → tag: category=network
 │    └── VPC
 │
 └── ApplicationStack → tag: category=application  (priority=200, overrides lower-priority rules)
      ├── EC2 t3.micro
      │   ├── tag: category=web-server          (resource-level)
      │   ├── tag: subcategory=primary          (EC2 instances only)
      │   └── tag: subcategory=side             (all EXCEPT EC2, priority=300)
      │   └── role — subcategory tag removed
      └── Elastic IP, NGINX, S3 asset, Security Groups
```

---

## Stacks

### `NetworkStack` — `cdk_stack_tagging/network_stack.py`

Same as `cdk_multi_stacks/network_stack.py`. Creates a VPC and exposes it as `self.vpc`.

| Resource | Notes |
|---|---|
| VPC | `ec2.Vpc`, `nat_gateways=0` |
| Stack-level tag | `category=network` applied to all resources in this stack |

### `ApplicationStack` — `cdk_stack_tagging/application_stack.py`

Same EC2/NGINX infrastructure as `cdk_multi_stacks/application_stack.py`, extended with resource-level tag demonstrations.

| Resource | Configuration | Notes |
|---|---|---|
| EC2 Instance | `t3.micro`, Amazon Linux 2023 | Multiple tags applied at different scopes and priorities |
| Elastic IP | `ec2.CfnEIP` | Inherits stack-level `category=application` tag |
| NGINX | Installed via user data | Serves custom HTML page |
| S3 Asset | `s3_assets.Asset` | Custom HTML from `cdk_s3_assets/web_pages/index.html` |
| Security Group | TCP 80 + TCP 22 | Managed by `web_server.connections` |

#### CloudFormation Outputs

| Output | Description |
|---|---|
| `WebServerPublicIP` | Public IP address of the EC2 instance |
| `WebServerPublicDNS` | Public DNS name of the EC2 instance |

---

## Project Structure

```
cdk_stack_tagging/
├── app.py                                      # Entry point: stacks + stack-level tagging
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
└── cdk_stack_tagging/
    ├── __init__.py
    ├── network_stack.py                        # NetworkStack: VPC
    └── application_stack.py                   # ApplicationStack: EC2, NGINX, granular tagging
```

---

## Tagging Patterns Demonstrated

### 1. Stack-level tags (`app.py`)

```python
# Applies category=network to ALL resources in NetworkStack
cdk.Tags.of(network_stack).add("category", "network")

# Applies category=application to ALL resources in ApplicationStack
# priority=200 means this tag wins over any lower-priority tag with the same key
cdk.Tags.of(application_stack).add("category", "application", priority=200)
```

### 2. Resource-level tags (`application_stack.py`)

```python
# Tag applied to the EC2 instance (and everything it owns)
Tags.of(web_server).add("category", "web-server")

# Tag applied ONLY to AWS::EC2::Instance resources
Tags.of(web_server).add("subcategory", "primary",
    include_resource_types=["AWS::EC2::Instance"])

# Tag applied to everything EXCEPT AWS::EC2::Instance, at a higher priority
Tags.of(web_server).add("subcategory", "side",
    exclude_resource_types=["AWS::EC2::Instance"],
    priority=300)
```

### 3. Removing a tag

```python
# Removes the "subcategory" tag from the EC2 instance's IAM role
Tags.of(web_server.role).remove("subcategory")
```

---

## Tag Priority Rules

| Priority | Higher value wins |
|---|---|
| Default | `100` |
| `priority=200` | Overrides the default stack-level tag |
| `priority=300` | Overrides `priority=200` for matching resource types |

When two rules assign the **same tag key** to the same resource, the rule with the **higher `priority` value** wins.

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
cd cdk_stack_tagging

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate.bat     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Bootstrap your AWS environment (first time only, per account/region)
cdk bootstrap

# 5. Preview the synthesised template and inspect tags in the JSON output
cdk synth

# 6. Deploy to AWS
cdk deploy --all

# 7. Verify tags in the AWS Console (EC2 → Tags tab) or via CLI:
aws ec2 describe-instances --query 'Reservations[*].Instances[*].Tags'

# 8. Tear down all resources when done
cdk destroy --all
```

---

## Key Concepts

| Concept | Description |
|---|---|
| `cdk.Tags.of(scope).add(key, value)` | Applies a tag to all taggable resources within the given scope |
| `priority=` | Integer (default 100); higher priority wins when tag keys conflict |
| `include_resource_types=[]` | Restricts the tag to a specific list of CloudFormation resource types |
| `exclude_resource_types=[]` | Applies the tag to all resource types except those listed |
| `Tags.of(scope).remove(key)` | Removes a previously applied tag from all resources in the scope |

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Same two-stack architecture (no tagging) | [`cdk_multi_stacks`](../cdk_multi_stacks/README.md) |
| Same architecture as nested stacks | [`cdk_nested_stacks`](../cdk_nested_stacks/README.md) |
| S3 asset deployment (shared by this project) | [`cdk_s3_assets`](../cdk_s3_assets/README.md) |
