import jsii
from aws_cdk import (
    Stack,
    Aspects,
    IAspect,
    Annotations,
    aws_ec2 as ec2,
)


@jsii.implements(IAspect)
class EC2InstanceTypeChecker:
    # This class defines a custom aspect that implements the IAspect interface. 
    # The visit method is called for each node in the CDK construct tree.
    def visit(self, node):
        # Check if the current node is an EC2 instance.
        if isinstance(node, ec2.CfnInstance):
            # If it is an EC2 instance, check the instance type.
            if node.instance_type not in ["t2.micro", "t3.micro"]:
                # If the instance type is not t2.micro or t3.micro, add an error annotation to the node.
                Annotations.of(node).add_warning(
                    f"EC2 instance {node.instance_type} is invalid. It will be set to t3.micro."
                )
                # ! NOTE: Changing resources automatically in an aspect is generally not recommended, 
                # ! as it can lead to unexpected behavior.
                # Automatically change the instance type to t3.micro if it's not valid.
                node.instance_type = "t3.micro" 
                

@jsii.implements(IAspect)
class SSHAnywhereChecker:
    # This class defines another custom aspect that checks for security groups allowing SSH access from anywhere.
    def visit(self, node):
        # Check if the current node is a security group.
        if isinstance(node, ec2.CfnSecurityGroup):
            print(node.security_group_ingress)
            # Check each ingress rule in the security group.
            rules = Stack.of(node).resolve(node.security_group_ingress)
            # If any rule allows SSH access (port 22) from anywhere (
            for rule in rules:
                if rule.get("ipProtocol") == "tcp" and rule.get("fromPort") <= 22 and rule.get("toPort") >= 22:
                    cidr_ip = rule.get("cidrIp")
                    if cidr_ip == "0.0.0.0/0":
                        # If such a rule is found, add a warning annotation to the node.
                        Annotations.of(node).add_warning(
                            "Security group allows SSH access from anywhere. This is not recommended for production environments."
                        )