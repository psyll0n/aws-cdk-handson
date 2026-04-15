#!/usr/bin/env python3
import os

import aws_cdk as cdk


from cdk_nested_stacks.network_stack import NetworkStack
from cdk_nested_stacks.application_stack import ApplicationStack

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
ApplicationStack(root_stack, "ApplicationStack", main_vpc=network_stack.vpc)

# Synthesize the CloudFormation template for the entire application, which includes both the root stack and its nested stacks.
app.synth()
