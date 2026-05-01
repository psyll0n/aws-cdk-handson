# cdk\_multi\_stacks — Multiple CDK Stacks with Cross-Stack References

Demonstrates how to split a CDK application into **multiple independent CloudFormation stacks** that share resources via cross-stack references. The VPC is owned and exported by `NetworkStack`; `ApplicationStack` consumes it by accepting the VPC as a constructor parameter.

---

## What You Will Learn

- How to define multiple top-level CDK stacks in a single `app.py`
- How to share a resource (VPC) between stacks via a Python constructor parameter
- How CDK generates CloudFormation `Exports` and `Fn::ImportValue` under the hood
- The difference between multi-stack (independent CFN stacks) and nested-stack (one root stack) patterns
- How to deploy and destroy individual stacks with `cdk deploy <StackName>`

---

## Architecture

```
app.py
 ├── NetworkStack     (CloudFormation stack 1)
 │    └── VPC ──────────────────────────────────────────┐ cross-stack reference
 │                                                       │
 └── ApplicationStack (CloudFormation stack 2)          │
      ├── EC2 t3.micro (Amazon Linux 2023) ◄────────────┘ (uses VPC from NetworkStack)
      │   ├── NGINX (via user data)
      │   ├── Elastic IP
      │   └── Serves index.html (from S3 asset)
      └── Security Groups: TCP 80, TCP 22
```

---

## Stacks

### `NetworkStack` — `cdk_multi_stacks/network_stack.py`

Creates the shared networking layer and exposes the VPC as a public attribute.

| Resource | Notes |
|---|---|
| VPC | `ec2.Vpc`, `nat_gateways=0`; public subnets auto-created; exposed as `self.vpc` |

### `ApplicationStack` — `cdk_multi_stacks/application_stack.py`

Receives `main_vpc` from `NetworkStack` and deploys the web server.

| Resource | Configuration | Notes |
|---|---|---|
| EC2 Instance | `t3.micro`, Amazon Linux 2023 | Placed in the public subnet of the shared VPC |
| Elastic IP | `ec2.CfnEIP` | Stable public IP |
| NGINX | Installed via user data | Serves the custom HTML page |
| S3 Asset | `s3_assets.Asset` (from `cdk_s3_assets/web_pages/index.html`) | Custom HTML downloaded to the instance at boot |
| Security Group | TCP 80 + TCP 22 from `0.0.0.0/0` | Managed by `web_server.connections` |

#### CloudFormation Outputs

| Output | Description |
|---|---|
| `WebServerPublicIP` | Public IP address of the EC2 instance |
| `WebServerPublicDNS` | Public DNS name of the EC2 instance |

---

## Project Structure

```
cdk_multi_stacks/
├── app.py                                      # Entry point: creates NetworkStack then ApplicationStack
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
├── web_pages/
│   └── index.html                             # Static HTML served by NGINX
└── cdk_multi_stacks/
    ├── __init__.py
    ├── network_stack.py                        # NetworkStack: VPC
    └── application_stack.py                   # ApplicationStack: EC2, NGINX, S3 asset
```

---

## Cross-Stack Reference Pattern

```python
# app.py — the key pattern
network_stack = NetworkStack(app, "NetworkStack")

# The VPC object is passed directly; CDK generates a CFN Export/Import pair
ApplicationStack(app, "ApplicationStack", main_vpc=network_stack.vpc)
```

CDK converts `network_stack.vpc` into a CloudFormation `Export` in `NetworkStack` and an `Fn::ImportValue` in `ApplicationStack`. This means the two stacks are **deployed as separate CloudFormation stacks** but share a live cross-stack dependency.

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
cd cdk_multi_stacks

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate.bat     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Bootstrap your AWS environment (first time only, per account/region)
cdk bootstrap

# 5. Preview both stacks
cdk synth

# 6. Deploy all stacks (order is resolved automatically by CDK)
cdk deploy --all

# — or deploy them individually in dependency order:
cdk deploy NetworkStack
cdk deploy ApplicationStack

# 7. Verify NGINX is serving the page
curl http://<WebServerPublicIP>

# 8. Tear down all resources when done (reverse order)
cdk destroy --all
```

---

## Key Concepts

| Concept | Description |
|---|---|
| Multiple stacks in one app | Each `Stack` instance in `app.py` becomes a separate CloudFormation stack |
| Cross-stack reference | Passing a CDK construct (e.g., VPC) between stacks generates CFN Export/ImportValue |
| Stack dependency | CDK automatically detects the dependency and deploys `NetworkStack` first |
| `cdk deploy --all` | Deploys all stacks respecting dependency order |

---

## Multi-Stack vs Nested-Stack

| | Multi-Stack (`cdk_multi_stacks`) | Nested-Stack (`cdk_nested_stacks`) |
|---|---|---|
| CloudFormation topology | Two independent root stacks | One root stack containing two nested stacks |
| Cross-stack wiring | CloudFormation `Export` / `ImportValue` | Direct Python reference (no CFN exports) |
| Independent deployability | Yes — deploy/update each stack separately | No — all nested stacks deploy with the parent |
| Use case | Large apps, separate team ownership | Logically grouped resources, single deployment unit |

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Same architecture with nested stacks | [`cdk_nested_stacks`](../cdk_nested_stacks/README.md) |
| Same architecture with tagging | [`cdk-stack-tagging`](../cdk-stack-tagging/README.md) |
| S3 asset deployment (shared by this project) | [`cdk_s3_assets`](../cdk_s3_assets/README.md) |
