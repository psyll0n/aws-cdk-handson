# l2\_cdk\_constructs — VPC Networking with L2 (Higher-Level) Constructs

Contrasts directly with [`l1_cdk_constructs`](../l1_cdk_constructs/README.md) by recreating equivalent VPC infrastructure using **L2 CDK constructs**. L2 constructs provide opinionated, higher-level abstractions with sensible defaults, reducing dozens of lines of L1 boilerplate to just a few.

---

## What You Will Learn

- What L2 (Layer 2) CDK constructs are and how they differ from L1
- How `ec2.Vpc` automatically provisions subnets, route tables, and Internet Gateway attachments
- How to control topology options (`nat_gateways`, `max_azs`, `subnet_configuration`)
- Why L2 constructs are preferred for most production CDK code

---

## Architecture

```
VPC  (auto-assigned CIDR, up to 3 AZs)
├── Public Subnet  ×3  (one per AZ — with IGW route, auto-assigned public IPs)
└── Private Subnet ×3  (one per AZ — no NAT gateway because nat_gateways=0)
```

> CDK automatically creates the Internet Gateway, subnets, and route tables. No NAT Gateways are deployed (`nat_gateways=0`), keeping AWS costs at zero for this demo.

---

## AWS Resources Created

| Resource | How it is created | Notes |
|---|---|---|
| VPC | `ec2.Vpc` L2 construct | CDK-managed CIDR |
| Internet Gateway | Auto-created by `ec2.Vpc` | Attached and routed for public subnets |
| Public Subnets | Auto-created by `ec2.Vpc` | Up to 3 (one per AZ), public IPs enabled |
| Private Subnets | Auto-created by `ec2.Vpc` | Up to 3 (one per AZ), no outbound NAT |
| Route Tables | Auto-created by `ec2.Vpc` | One per subnet, properly configured |

---

## Project Structure

```
l2_cdk_constructs/
├── app.py                                      # CDK application entry point
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
└── l2_cdk_constructs/
    ├── __init__.py
    └── l2_cdk_constructs_stack.py              # Stack: VPC using ec2.Vpc L2 construct
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
cd l2_cdk_constructs

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
| L2 constructs | Higher-level abstractions that implement AWS best practices by default |
| `ec2.Vpc` | Creates a complete VPC topology automatically |
| `nat_gateways=0` | Disables NAT Gateways (saves cost; private subnets lose outbound internet access) |
| `max_azs=3` | Spreads subnets across up to 3 availability zones for resilience |

---

## L1 vs L2 at a Glance

```
# L1 (l1_cdk_constructs) — ~50 lines for the same topology:
vpc = ec2.CfnVPC(...)
igw = ec2.CfnInternetGateway(...)
ec2.CfnVPCGatewayAttachment(...)
# + 4 subnets, 4 route tables, 4 associations, 2 routes ...

# L2 (this project) — 4 lines:
vpc = ec2.Vpc(self, "VPCPrimary",
              nat_gateways=0,
              max_azs=3)
```

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Same VPC with L1 / raw CloudFormation constructs | [`l1_cdk_constructs`](../l1_cdk_constructs/README.md) |
| Serverless app built on L2 constructs | [`l2_serverless_app`](../l2_serverless_app/README.md) |
| Full networking stack (VPC + EC2 + RDS) | [`cdk_networking`](../cdk_networking/README.md) |
