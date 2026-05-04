# cdk\_testing — CDK Unit Testing with aws-cdk.assertions

Demonstrates how to write **unit tests for CDK stacks** using the `aws_cdk.assertions` module. The infrastructure mirrors the [`cdk_nested_stacks`](../cdk_nested_stacks/README.md) project (a nested-stack VPC + EC2/NGINX application), and the test suite validates resource counts, instance type, and security group rules — all without deploying to AWS.

---

## What You Will Learn

- How to use `aws_cdk.assertions.Template` to inspect a synthesised CloudFormation template
- How to assert resource counts with `template.resource_count_is()`
- How to assert resource properties with `template.has_resource_properties()`
- How to use `assertions.Match` helpers (`string_like_regexp`, `any_value`, `absent`, `array_with`, `object_like`) for flexible, partial assertions
- How to wire nested stacks together in a test fixture

---

## Architecture

The stacks under test are identical to `cdk_nested_stacks`:

```
app.py
 └── RootStack  (single top-level CloudFormation stack)
      ├── NetworkStack  (Stack)
      │    └── VPC (nat_gateways=0)
      │
      └── ApplicationStack  (Stack)
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
| VPC | `ec2.Vpc`, `nat_gateways=0` | Created in `NetworkStack` |
| EC2 Instance | `t3.micro`, Amazon Linux 2023 | Public subnet; NGINX + custom HTML at boot |
| Elastic IP | `ec2.CfnEIP` | Stable public IP |
| S3 Asset | `s3_assets.Asset` | `web_pages/index.html` from `cdk_s3_assets/` |

---

## Project Structure

```
cdk_testing/
├── app.py                                      # CDK application entry point
├── cdk.json                                    # CDK toolkit configuration
├── requirements.txt                            # Runtime dependencies
├── requirements-dev.txt                        # Dev/test dependencies (pytest, aws-cdk assertions)
├── source.bat                                  # Windows venv helper
└── cdk_testing/
│   ├── __init__.py
│   ├── network_stack.py                        # NetworkStack: VPC
│   └── application_stack.py                   # ApplicationStack: EC2, NGINX, S3 asset
└── tests/
    └── unit/
        └── test_cdk_testing_stack.py           # Unit tests using aws_cdk.assertions
```

---

## Test Cases

### `test_network_stack_resource_counts`

Asserts that `NetworkStack` synthesises exactly one VPC and zero NAT Gateways.

```python
template.resource_count_is("AWS::EC2::VPC", 1)
template.resource_count_is("AWS::EC2::NatGateway", 0)
```

### `test_application_stack_web_server`

Asserts that the EC2 instance in `ApplicationStack` uses a `t2.micro` or `t3.micro` instance type, has no key pair set, and has a valid AMI.

```python
template.has_resource_properties("AWS::EC2::Instance", {
    'InstanceType': assertions.Match.string_like_regexp('(t2|t3).micro'),
    'ImageId': assertions.Match.any_value(),
    'KeyName': assertions.Match.absent(),
})
```

### `test_web_server_security_group`

Asserts that the security group allows inbound TCP traffic on port 80 from `0.0.0.0/0`.

```python
template.has_resource_properties("AWS::EC2::SecurityGroup", {
    'SecurityGroupIngress': assertions.Match.array_with([
        assertions.Match.object_like({
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'CidrIp': '0.0.0.0/0',
        })
    ]),
})
```

---

## Prerequisites

- Python 3.8+
- Node.js (required by the CDK CLI)
- AWS CDK CLI — `npm install -g aws-cdk`
- AWS credentials are **not required** to run unit tests (no deployment happens)

---

## Setup & Running Tests

```bash
# 1. Navigate into this project
cd cdk_testing

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate.bat     # Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Run the unit tests
pytest tests/unit/

# 5. Run with verbose output
pytest tests/unit/ -v
```

No `cdk bootstrap` or `cdk deploy` is needed — all tests run locally by synthesising the template in memory.

---

## Key Concepts

| Concept | Description |
|---|---|
| `assertions.Template.from_stack()` | Synthesises a CDK stack and wraps the resulting CloudFormation JSON for inspection |
| `resource_count_is(type, count)` | Asserts that exactly `count` resources of `type` exist in the template |
| `has_resource_properties(type, props)` | Asserts that at least one resource of `type` has the given properties (partial match) |
| `Match.string_like_regexp(pattern)` | Matches a string property against a regular expression |
| `Match.any_value()` | Accepts any non-null value — useful for AMI IDs or generated identifiers |
| `Match.absent()` | Asserts that a property is **not** present in the resource |
| `Match.array_with([...])` | Asserts that an array contains all listed items (other items may also be present) |
| `Match.object_like({...})` | Asserts that an object contains all listed keys (other keys may also be present) |

---

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
