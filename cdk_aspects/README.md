# cdk-aspects — Custom CDK Aspects for Compliance & Governance

Introduces **CDK Aspects** — a powerful mechanism that lets you visit every node in the CDK construct tree and inspect, annotate, or mutate resources at synthesis time. This project implements a custom `EC2InstanceTypeChecker` aspect that enforces an allowed list of EC2 instance types across an entire stack, and combines it with the nested-stack architecture and tagging patterns from earlier projects.

---

## What You Will Learn

- What CDK Aspects are and how they fit into the CDK lifecycle
- How to implement the `IAspect` interface with `@jsii.implements`
- How the `visit(node)` method is called for every construct in the tree
- How to use `Annotations` to emit warnings on non-compliant resources
- How to mutate a CloudFormation resource property inside an aspect
- How to attach an aspect to a scope with `cdk.Aspects.of(scope).add(...)`
- How aspects compose with tagging and nested stacks

---

## Architecture

```
app.py
 └── RootStack  (single top-level CloudFormation stack)
      │
      │  EC2InstanceTypeChecker Aspect ← applied to entire RootStack
      │  (visits every node; warns & fixes non-t2/t3.micro instances)
      │
      ├── NetworkStack  (NestedStack)   tag: category=network
      │    └── VPC (nat_gateways=0)
      │
      └── ApplicationStack  (NestedStack)   tag: category=application (priority=200)
           ├── EC2 t3.micro (Amazon Linux 2023)
           │   ├── NGINX (via user data)
           │   ├── Elastic IP
           │   └── Serves index.html (from S3 asset)
           └── Security Groups: TCP 80, TCP 22
```

---

## AWS Resources Created

| Resource | Configuration | Notes |
|---|---|---|
| VPC | `ec2.Vpc`, `nat_gateways=0` | Created inside `NetworkStack` (NestedStack) |
| EC2 Instance | `t3.micro`, Amazon Linux 2023 | Public subnet; NGINX + custom HTML at boot |
| Elastic IP | `ec2.CfnEIP` | Stable public IP for the instance |
| S3 Asset | `s3_assets.Asset` | `web_pages/index.html` uploaded by CDK, downloaded at boot |
| IAM Policy | Auto-granted by `grant_read()` | EC2 role can read the asset from S3 |

### CloudFormation Outputs

| Output | Description |
|---|---|
| `WebServerPublicIP` | Public IP address of the EC2 instance |
| `WebServerPublicDNS` | Public DNS name of the EC2 instance |

---

## Project Structure

```
cdk-aspects/
├── app.py                                      # Entry point: stacks, aspect attachment, tagging
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies
├── source.bat                                  # Windows venv helper
├── web_pages/
│   └── index.html                             # Static HTML served by NGINX
└── cdk_aspects/
    ├── __init__.py
    ├── aspects.py                             # EC2InstanceTypeChecker — the custom CDK Aspect
    ├── network_stack.py                        # NetworkStack (NestedStack): VPC
    └── application_stack.py                   # ApplicationStack (NestedStack): EC2, NGINX, S3 asset
```

---

## The Custom Aspect — `EC2InstanceTypeChecker`

Defined in `cdk_aspects/aspects.py`:

```python
@jsii.implements(IAspect)
class EC2InstanceTypeChecker:
    def visit(self, node):
        if isinstance(node, ec2.CfnInstance):
            if node.instance_type not in ["t2.micro", "t3.micro"]:
                Annotations.of(node).add_warning(
                    f"EC2 instance {node.instance_type} is invalid. "
                    f"It will be set to t3.micro."
                )
                node.instance_type = "t3.micro"   # auto-correct
```

### How it works

| Step | What happens |
|---|---|
| `@jsii.implements(IAspect)` | Declares this Python class as a CDK Aspect to the JSII runtime |
| `visit(node)` | Called once for **every construct** in the scope the aspect is applied to |
| `isinstance(node, ec2.CfnInstance)` | Filters down to only L1 EC2 instance resources |
| `Annotations.of(node).add_warning()` | Emits a synthesis-time warning visible in `cdk synth` and `cdk deploy` output |
| `node.instance_type = "t3.micro"` | Mutates the CloudFormation property directly — the deployed template uses `t3.micro` regardless of what the stack code specified |

### Aspect attachment

```python
# app.py — attach the aspect to the root stack
# It will visit every construct nested inside RootStack
cdk.Aspects.of(root_stack).add(EC2InstanceTypeChecker())
```

---

## Aspect Lifecycle in CDK

```
cdk synth / cdk deploy
        │
        ▼
  1. Construct tree is built  (all Stack / NestedStack / Resource objects created)
        │
        ▼
  2. Aspects are invoked       ← EC2InstanceTypeChecker.visit() runs here
     (DFS traversal of the tree; visit() called for each node)
        │
        ▼
  3. Template is synthesised   (CloudFormation JSON produced with any mutations applied)
```

Aspects run **after** the construct tree is fully assembled but **before** the CloudFormation template is finalised, making them ideal for cross-cutting concerns like compliance checks, enforced encryption, or tag auditing.

---

## Tagging

Stack-level tags are applied in `app.py`, composing with the aspect:

```python
cdk.Tags.of(network_stack).add("category", "network")
cdk.Tags.of(application_stack).add("category", "application", priority=200)
```

See [`cdk-stack-tagging`](../cdk-stack-tagging/README.md) for a full breakdown of the CDK tagging API.

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
cd cdk-aspects

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate.bat     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Bootstrap your AWS environment (first time only, per account/region)
cdk bootstrap

# 5. Synthesize — aspect warnings appear here if instance types are non-compliant
cdk synth

# 6. Deploy to AWS
cdk deploy RootStack

# 7. Verify NGINX is serving the page
curl http://<WebServerPublicIP>

# 8. Tear down all resources when done
cdk destroy RootStack
```

### Triggering the aspect warning

To see the aspect in action, temporarily change the instance type in `application_stack.py` to something outside the allowed list (e.g. `ec2.InstanceSize.LARGE`), then run `cdk synth`. You will see:

```
[Warning at /RootStack/ApplicationStack/WebServer/Resource]
EC2 instance m5.large is invalid. It will be set to t3.micro.
```

The synthesised template will still contain `t3.micro`.

---

## Key Concepts

| Concept | Description |
|---|---|
| `IAspect` | CDK interface with a single `visit(node)` method |
| `@jsii.implements(IAspect)` | Tells the JSII runtime that the Python class satisfies the `IAspect` contract |
| `cdk.Aspects.of(scope).add(aspect)` | Registers an aspect to be applied to all constructs within `scope` |
| `Annotations.of(node).add_warning()` | Emits a synthesis-time warning attached to a specific construct |
| `Annotations.of(node).add_error()` | Would halt synthesis entirely — useful for hard compliance failures |
| Construct tree traversal | Aspects perform a depth-first traversal; every node in the scope is visited |
| Aspect mutation | Properties set inside `visit()` are reflected in the final CloudFormation template |

---

## When to Use Aspects

| Use case | Example |
|---|---|
| Compliance enforcement | Block or warn on unapproved instance types, unencrypted volumes, open security groups |
| Automatic remediation | Force encryption, correct misconfigured properties at synthesis time |
| Cross-cutting tagging | Apply mandatory tags to every resource across all stacks |
| Auditing | Log or collect information about all resources in the tree |

---

## Related Projects

← Back to the [repository root](../README.md)

| Related | Project |
|---|---|
| Nested stacks (base architecture) | [`cdk_nested_stacks`](../cdk_nested_stacks/README.md) |
| Stack & resource tagging (also used here) | [`cdk-stack-tagging`](../cdk-stack-tagging/README.md) |
| S3 asset deployment (shared by this project) | [`cdk_s3_assets`](../cdk_s3_assets/README.md) |
