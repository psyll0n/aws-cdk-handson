# cdk\_s3\_assets — Deploying Static Files to EC2 via S3 Assets

Demonstrates the **CDK S3 Assets** feature: packaging a local file at synthesis time, uploading it to an S3 bucket during deployment, and having the EC2 instance automatically download and serve it via a signed URL embedded in user data.

---

## What You Will Learn

- What CDK S3 assets are and how they differ from manually uploading files
- How `s3_assets.Asset` packages a local file and uploads it during `cdk deploy`
- How `add_s3_download_command()` injects a signed S3 download into EC2 user data
- How CDK automatically grants the EC2 instance role read access to the asset bucket
- How to serve a custom HTML page from NGINX on EC2

---

## Architecture

```
  cdk deploy
      │
      │  1. CDK packages web_pages/index.html
      │     and uploads it to an S3 bucket
      │
      ▼
┌────────────────────────────────────────────────────┐
│  VPC (CDK-managed, no NAT Gateways)               │
│                                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  EC2 t3.micro  (Amazon Linux 2023)           │  │
│  │  [Elastic IP]                                │  │
│  │                                              │  │
│  │  User Data (boot sequence):                  │  │
│  │    1. dnf install nginx                      │  │
│  │    2. aws s3 cp s3://<bucket>/index.html \   │  │
│  │           /usr/share/nginx/html/index.html   │  │  ◄── 2. download from S3
│  │    3. systemctl start nginx                  │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
              │  Port 80
              ▼
         Browser / curl
```

---

## AWS Resources Created

| Resource | Configuration | Notes |
|---|---|---|
| VPC | `ec2.Vpc`, `nat_gateways=0` | Public subnets auto-created |
| EC2 Instance | `t3.micro`, Amazon Linux 2023 | Public subnet; NGINX + custom HTML served at boot |
| Elastic IP | `ec2.CfnEIP` | Stable public IP for the instance |
| S3 Asset | `s3_assets.Asset` | Local `web_pages/index.html` packaged and uploaded by CDK |
| IAM Policy | Auto-granted by `grant_read()` | EC2 instance role can read the asset from S3 |

### CloudFormation Outputs

| Output | Description |
|---|---|
| `WebServerPublicIP` | Public IP address of the EC2 instance |
| `WebServerPublicDNS` | Public DNS name of the EC2 instance |

---

## Project Structure

```
cdk_s3_assets/
├── app.py                                      # CDK application entry point
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
├── web_pages/
│   └── index.html                             # Static HTML page served by NGINX
└── cdk_s3_assets/
    ├── __init__.py
    └── cdk_s3_assets_stack.py                 # Stack: VPC, EC2, EIP, S3 asset deployment
```

---

## How S3 Asset Deployment Works

```python
# 1. Declare the asset — CDK packages and uploads the file during cdk deploy
web_page_asset = s3_assets.Asset(self, "WebPageAsset",
    path="../cdk_s3_assets/web_pages/index.html")

# 2. Inject a signed download command into EC2 user data
web_server.user_data.add_s3_download_command(
    bucket=web_page_asset.bucket,
    bucket_key=web_page_asset.s3_object_key,
    local_file="/usr/share/nginx/html/index.html"
)

# 3. Grant the instance role read permission on the asset bucket
web_page_asset.grant_read(web_server.role)
```

At deploy time CDK synthesises an `aws s3 cp` command with a pre-signed URL and embeds it in the instance's user data script.

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
cd cdk_s3_assets

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate.bat     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Bootstrap your AWS environment (first time only, per account/region)
#    Bootstrapping creates the S3 staging bucket used by CDK Assets
cdk bootstrap

# 5. Preview the CloudFormation template (asset is also uploaded here)
cdk synth

# 6. Deploy to AWS
cdk deploy

# 7. Verify the custom page is served
curl http://<WebServerPublicIP>

# 8. Tear down all resources when done
cdk destroy
```

---

## Key Concepts

| Concept | Description |
|---|---|
| `s3_assets.Asset` | Packages a local file/directory and uploads it to the CDK bootstrap S3 bucket |
| `add_s3_download_command()` | Inserts an authenticated `aws s3 cp` into EC2 user data |
| `grant_read()` | Adds an IAM policy allowing the EC2 role to read from the asset bucket |
| `user_data_causes_replacement=True` | Forces instance replacement (not just reboot) when user data changes |
| CDK bootstrap bucket | The S3 bucket created by `cdk bootstrap` that stores all CDK assets |

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Same EC2 + S3 asset pattern split across multiple stacks | [`cdk_multi_stacks`](../cdk_multi_stacks/README.md) |
| Same pattern inside nested stacks | [`cdk_nested_stacks`](../cdk_nested_stacks/README.md) |
| EC2 + RDS networking stack | [`cdk_networking`](../cdk_networking/README.md) |
