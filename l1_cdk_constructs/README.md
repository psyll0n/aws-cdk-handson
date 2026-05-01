# l1\_cdk\_constructs — VPC Networking with L1 (CloudFormation) Constructs

Demonstrates the lowest level of CDK abstraction: **L1 constructs** (prefixed with `Cfn`). These are direct, one-to-one mappings to raw CloudFormation resource types, giving you complete control over every property at the cost of more verbose code.

---

## What You Will Learn

- What L1 (Layer 1 / `Cfn*`) CDK constructs are and when to use them
- How to manually wire together every piece of a VPC: subnets, route tables, an Internet Gateway, and gateway attachments
- How CDK resolves cross-resource references (e.g. `vpc.attr_vpc_id`)
- The contrast between verbose L1 code and the concise L2 equivalent (see [`l2_cdk_constructs`](../l2_cdk_constructs/README.md))

---

## Architecture

```
VPC  10.0.0.0/16
├── Internet Gateway  (attached to VPC)
│
├── Public Subnet 1   10.0.0.0/24  (AZ 1)  ── Route Table ──► IGW (0.0.0.0/0)
├── Public Subnet 2   10.0.1.0/24  (AZ 2)  ── Route Table ──► IGW (0.0.0.0/0)
├── Private Subnet 1  10.0.2.0/24  (AZ 1)  ── Route Table  (local only)
└── Private Subnet 2  10.0.3.0/24  (AZ 2)  ── Route Table  (local only)
```

---

## AWS Resources Created

| Resource | CDK L1 Construct | Notes |
|---|---|---|
| VPC | `ec2.CfnVPC` | `10.0.0.0/16`, DNS support + hostnames enabled |
| Internet Gateway | `ec2.CfnInternetGateway` | One IGW for the VPC |
| IGW Attachment | `ec2.CfnVPCGatewayAttachment` | Attaches the IGW to the VPC |
| Subnet ×4 | `ec2.CfnSubnet` | 2 public (`map_public_ip_on_launch=True`), 2 private |
| Route Table ×4 | `ec2.CfnRouteTable` | One per subnet |
| Route Table Association ×4 | `ec2.CfnSubnetRouteTableAssociation` | Binds each subnet to its route table |
| Default Route (public only) ×2 | `ec2.CfnRoute` | `0.0.0.0/0 → IGW` for each public subnet |

---

## Project Structure

```
l1_cdk_constructs/
├── app.py                                      # CDK application entry point
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
└── l1_cdk_constructs/
    ├── __init__.py
    └── l1_cdk_constructs_stack.py              # Stack: VPC built entirely with CfnXxx constructs
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
cd l1_cdk_constructs

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
| L1 constructs (`Cfn*`) | Direct CloudFormation resource wrappers — full control, zero magic |
| `attr_vpc_id` / `attr_*` | CDK token references that resolve at synthesis time to CloudFormation `!Ref` / `!GetAtt` |
| `CfnSubnetRouteTableAssociation` | Explicitly binds a subnet to a route table (done automatically by L2) |
| `CfnRoute` | Adds a route to a route table (e.g., default route via IGW) |

---

## L1 vs L2 Comparison

The same VPC topology can be expressed in **~5 lines** with L2 constructs:

```python
# L1 — this project: ~50 lines for 4 subnets + IGW + route tables + associations
# L2 — see l2_cdk_constructs: 4 lines total
vpc = ec2.Vpc(self, "VPCPrimary", nat_gateways=0, max_azs=3)
```

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Same VPC with L2 constructs (concise) | [`l2_cdk_constructs`](../l2_cdk_constructs/README.md) |
| Full networking stack (VPC + EC2 + RDS) | [`cdk_networking`](../cdk_networking/README.md) |
