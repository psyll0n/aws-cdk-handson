#!/usr/bin/env python3
import os

import aws_cdk as cdk


# This file defines the main entry point for the CDK application, where we create instances of our stacks
from cdk_aspects.network_stack import NetworkStack
# Import the ApplicationStack class from the application_stack.py file.
# This stack will define the resources for our application, such as the EC2 instance and security group.
from cdk_aspects.application_stack import ApplicationStack
# Import the custom aspect defined in the aspects.py file.
# This aspect will be applied to the CDK construct tree to perform operations on each node.
from cdk_aspects.aspects import EC2InstanceTypeChecker, SSHAnywhereChecker


# This file defines the main entry point for the CDK application, where we create instances of our stacks
# and synthesize the CloudFormation template.
app = cdk.App()

# Create the root stack to hold the nested stacks.
root_stack = cdk.Stack(app, "RootStack")

# Define the network stack and reference the root stack as its parent. 
# This stack will create the VPC and related networking resources.
network_stack = NetworkStack(root_stack, "NetworkStack")

# Define the application stack and reference the root stack as its parent.
# This stack will create the application resources, including an EC2 instance that serves a web page.
application_stack = ApplicationStack(root_stack, "ApplicationStack", main_vpc=network_stack.vpc)


# Aspect attachments
cdk.Aspects.of(root_stack).add(EC2InstanceTypeChecker())  # Attach the custom aspect to the root stack, which will apply it to all constructs within the stack.
cdk.Aspects.of(root_stack).add(SSHAnywhereChecker())  # Attach the custom aspect to the root stack, which will apply it to all constructs within the stack.

# Stack-level tagging
cdk.Tags.of(network_stack).add("category", "network")
cdk.Tags.of(application_stack).add("category", "application",
                                   priority=200)  # Higher priority tags will override lower priority tags if there are conflicts.



# Synthesize the CloudFormation template for the entire application, which includes both the root stack and its nested stacks.
app.synth()
