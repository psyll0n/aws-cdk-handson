# cdk\_networking — Full Networking Stack (VPC + EC2 + RDS)

A single-stack CDK application that demonstrates a realistic three-tier networking topology: a public VPC, an EC2 web server running NGINX in the public subnet, and a privately isolated PostgreSQL RDS database — all wired together with the correct security group rules.

---

## What You Will Learn

- How to build a complete VPC topology with CDK L2 constructs
- How to launch an EC2 instance and configure it at boot with **user data**
- How to attach an **Elastic IP** to ensure a stable public address
- How to provision an **RDS PostgreSQL** database in a private isolated subnet
- How to define fine-grained **security group rules** between resources
- How to emit **CloudFormation Outputs** for deployed resource endpoints

---

## Architecture

```
                        ┌────────────────────────────────────────────┐
                        │  VPC (CDK-managed, no NAT Gateways)        │
                        │                                            │
  Internet ─── Port 80 ─►  ┌──────────────────┐                     │
  Internet ─── Port 22 ─►  │  EC2 t3.micro    │                     │
                        │  │  Amazon Linux 23 │                     │
                        │  │  NGINX           │                     │
                        │  │  [Elastic IP]    │◄─ Public Subnet     │
                        │  └────────┬─────────┘                     │
                        │           │  Port 5432                     │
                        │           ▼                                │
                        │  ┌──────────────────┐                     │
                        │  │  RDS PostgreSQL  │◄─ Private Isolated  │
                        │  │  16, t3.micro    │   Subnet            │
                        │  │  20 GB           │                     │
                        │  └──────────────────┘                     │
                        └────────────────────────────────────────────┘
```

---

## AWS Resources Created

| Resource | Configuration | Notes |
|---|---|---|
| VPC | `ec2.Vpc`, `nat_gateways=0` | Public + private isolated subnets auto-created |
| EC2 Instance | `t3.micro`, Amazon Linux 2023 | Public subnet; NGINX installed via user data |
| Elastic IP | `ec2.CfnEIP` | Attached to the EC2 instance |
| Security Group (EC2) | Inbound TCP 80 + TCP 22 from `0.0.0.0/0` | Created automatically by `ec2.Instance` |
| RDS PostgreSQL | `t3.micro`, v16, 20 GB, `multi_az=False` | Private isolated subnet; `DESTROY` removal policy |
| Security Group (RDS) | Inbound TCP 5432 from EC2 instance | Allows EC2 → RDS connectivity only |

### CloudFormation Outputs

| Output | Description |
|---|---|
| `WebServerPublicIP` | Elastic IP of the EC2 web server |
| `WebServerPublicDNS` | Public DNS name of the EC2 instance |
| `DbInstanceEndpoint` | RDS endpoint hostname for database connections |

---

## Project Structure

```
cdk_networking/
├── app.py                                      # CDK application entry point
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
└── cdk_networking/
    ├── __init__.py
    └── cdk_networking_stack.py                 # Single stack: VPC, EC2, EIP, RDS, security groups
```

---

## EC2 User Data

On first boot the instance runs:

```bash
sudo dnf update -y
sudo dnf install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
sudo dnf install mysql -y   # MySQL client for DB troubleshooting
```

---

## Prerequisites

- Python 3.8+
- Node.js (required by the CDK CLI)
- AWS CDK CLI — `npm install -g aws-cdk`
- AWS credentials configured (`aws configure` or environment variables)

> **Cost note:** This stack provisions an RDS instance (`t3.micro`) which incurs ongoing charges. Remember to run `cdk destroy` when you are done.

---

## Setup & Deployment

```bash
# 1. Navigate into this project
cd cdk_networking

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

# 6. Deploy to AWS (may take ~10 minutes due to RDS provisioning)
cdk deploy

# 7. Verify NGINX is running
curl http://<WebServerPublicIP>

# 8. Tear down all resources when done
cdk destroy
```

---

## Key Concepts

| Concept | Description |
|---|---|
| `ec2.Vpc` | Automatically creates public, private, and isolated subnets across AZs |
| `ec2.SubnetType.PRIVATE_ISOLATED` | Subnet with no route to the internet — ideal for databases |
| `user_data.add_commands()` | Shell commands executed on first boot via EC2 User Data |
| `connections.allow_from()` | Creates a security group ingress rule between two CDK resources |
| `rds.DatabaseInstance` | L2 construct for a single-AZ RDS instance |
| `RemovalPolicy.DESTROY` | Deletes the RDS instance and its data when `cdk destroy` is run |

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| EC2 + static file deployment via S3 assets | [`cdk_s3_assets`](../cdk_s3_assets/README.md) |
| EC2 split into multiple stacks | [`cdk_multi_stacks`](../cdk_multi_stacks/README.md) |
| VPC built with L2 constructs only | [`l2_cdk_constructs`](../l2_cdk_constructs/README.md) |
