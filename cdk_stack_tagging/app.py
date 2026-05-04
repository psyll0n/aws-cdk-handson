#!/usr/bin/env python3
import os

import aws_cdk as cdk


from cdk_stack_tagging.network_stack import NetworkStack
from cdk_stack_tagging.application_stack import ApplicationStack

# This file defines the main entry point for the CDK application, where we create instances of our stacks
# and synthesize the CloudFormation template.
app = cdk.App()

# Create the network stack first to set up the VPC, then pass the VPC reference to the application stack.
network_stack = NetworkStack(app, "NetworkStack")

# Create the application stack and pass the VPC reference from the network stack. This is called cross-stack referencing, 
# where one stack can use resources defined in another stack.
application_stack = ApplicationStack(app, "ApplicationStack", main_vpc=network_stack.vpc)


# Stack-level tags can be added to all resources within a stack. 
# Here we add a tag both the network stack and application stacks.
cdk.Tags.of(network_stack).add("category", "network")
cdk.Tags.of(application_stack).add("category", "application",
                                   priority=200)  # Higher priority to override any lower priority tags


app.synth()