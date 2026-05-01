# cdk\_nested\_stacks — Infrastructure with CDK Nested Stacks

Mirrors the [`cdk_multi_stacks`](../cdk_multi_stacks/README.md) architecture but uses **CDK `NestedStack`** instead of independent top-level stacks. Both `NetworkStack` and `ApplicationStack` extend `NestedStack` and are parented inside a single `RootStack`, resulting in one root CloudFormation stack that contains nested stack resources.

---

## What You Will Learn

- What CDK `NestedStack` is and how it differs from a regular `Stack`
- How to parent nested stacks inside a root stack
- How cross-stack references work within a nested-stack hierarchy (direct Python references — no CFN Exports)
- The trade-offs between nested stacks and multiple independent stacks
- How the synthesised CloudFormation templates differ

---

## Architecture

```
app.py
 └── RootStack  (single top-level CloudFormation stack)
      ├── NetworkStack  (NestedStack)
      │    └── VPC ──────────────────────────────────────────┐ direct Python reference
      │                                                       │
      └── ApplicationStack  (NestedStack)                    │
           ├── EC2 t3.micro (Amazon Linux 2023) ◄────────────┘
           │   ├── NGINX (via user data)
           │   ├── Elastic IP
           │   └── Serves index.html (from S3 asset)
           └── Security Groups: TCP 80, TCP 22
```

---

## Stacks

### `NetworkStack` — `cdk_nested_stacks/network_stack.py`

Extends `NestedStack`. Creates the shared VPC and exposes it as `self.vpc`.

| Resource | Notes |
|---|---|
| VPC | `ec2.Vpc`, `nat_gateways=0`; exposed as `self.vpc` |

### `ApplicationStack` — `cdk_nested_stacks/application_stack.py`

Extends `NestedStack`. Receives `main_vpc` and deploys the web server.

| Resource | Configuration | Notes |
|---|---|---|
| EC2 Instance | `t3.micro`, Amazon Linux 2023 | Public subnet of the shared VPC |
| Elastic IP | `ec2.CfnEIP` | Stable public IP |
| NGINX | Installed via user data | Serves the custom HTML page |
| S3 Asset | `s3_assets.Asset` (from `cdk_s3_assets/web_pages/index.html`) | Custom HTML downloaded at boot |
| Security Group | TCP 80 + TCP 22 from `0.0.0.0/0` | Managed by `web_server.connections` |

#### CloudFormation Outputs

| Output | Description |
|---|---|
| `WebServerPublicIP` | Public IP address of the EC2 instance |
| `WebServerPublicDNS` | Public DNS name of the EC2 instance |

---

## Project Structure

```
cdk_nested_stacks/
├── app.py                                      # Entry point: RootStack > NetworkStack + ApplicationStack
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
└── cdk_nested_stacks/
    ├── __init__.py
    ├── network_stack.py                        # NetworkStack (NestedStack): VPC
    └── application_stack.py                   # ApplicationStack (NestedStack): EC2, NGINX, S3 asset
```

---

## Nested Stack Wiring Pattern

```python
# app.py — key pattern for nested stacks
root_stack = cdk.Stack(app, "RootStack")

# Both nested stacks receive root_stack as their scope (parent)
network_stack = NetworkStack(root_stack, "NetworkStack")

# VPC reference is passed directly — no CFN Export/ImportValue needed
ApplicationStack(root_stack, "ApplicationStack", main_vpc=network_stack.vpc)
```

Because all nested stacks share the same root parent, CDK can pass live Python object references across them without generating CloudFormation `Export`/`ImportValue` pairs.

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
cd cdk_nested_stacks

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

# 6. Deploy (only the root stack needs to be specified)
cdk deploy RootStack

# 7. Verify NGINX is serving the page
curl http://<WebServerPublicIP>

# 8. Tear down all resources when done
cdk destroy RootStack
```

---

## Key Concepts

| Concept | Description |
|---|---|
| `NestedStack` | A CDK construct that maps to a `AWS::CloudFormation::Stack` resource inside a parent stack |
| Root stack parent | Nested stacks are instantiated with the root stack (not `app`) as their `scope` |
| No CFN exports | References between nested stacks under the same root use Python objects; CDK avoids CloudFormation exports |
| Single deployment unit | All nested stacks are deployed together when the root stack is deployed |

---

## Nested Stack vs Multi-Stack

| | Nested Stack (`cdk_nested_stacks`) | Multi-Stack (`cdk_multi_stacks`) |
|---|---|---|
| CloudFormation topology | One root stack, nested stack resources inside | Two independent root stacks |
| Cross-stack wiring | Direct Python reference (no CFN exports) | CloudFormation `Export` / `ImportValue` |
| Independent deployability | No — all deploy with the parent | Yes — each stack can be deployed/updated separately |
| Use case | Logically grouped resources, single deployment unit | Large apps, separate team ownership or deployment cadences |

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Same architecture with independent stacks | [`cdk_multi_stacks`](../cdk_multi_stacks/README.md) |
| Same architecture with tagging | [`cdk-stack-tagging`](../cdk-stack-tagging/README.md) |
| S3 asset deployment (shared by this project) | [`cdk_s3_assets`](../cdk_s3_assets/README.md) |
