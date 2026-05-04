import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_testing.network_stack import NetworkStack
from cdk_testing.application_stack import ApplicationStack


# This test verifies that the correct number of resources are created in the network stack 
# and application stack.
def test_network_stack_resource_counts():
    app = core.App()
    
    # Create the root stack to hold the nested stacks.
    root_stack = core.Stack(app, "RootStack")

    # Define the network stack and reference the root stack as its parent. 
    # This stack will create the VPC and related networking resources.
    network_stack = NetworkStack(root_stack, "NetworkStack")

    # Define the application stack and reference the root stack as its parent.
    # This stack will create the application resources, including an EC2 instance that serves a web page.
    ApplicationStack(root_stack, "ApplicationStack", main_vpc=network_stack.vpc)
    
    template = assertions.Template.from_stack(network_stack)
    
    template.resource_count_is("AWS::EC2::VPC", 1)

    template.resource_count_is("AWS::EC2::NatGateway", 0)
    
    
# This test verifies that the correct resources are created in the network stack and application stack.
def test_application_stack_web_server():
    app = core.App()
    
    # Create the root stack to hold the nested stacks.
    root_stack = core.Stack(app, "RootStack")

    # Define the network stack and reference the root stack as its parent. 
    # This stack will create the VPC and related networking resources.
    network_stack = NetworkStack(root_stack, "NetworkStack")

    # Define the application stack and reference the root stack as its parent.
    # This stack will create the application resources, including an EC2 instance that serves a web page.
    application_stack = ApplicationStack(root_stack, "ApplicationStack", main_vpc=network_stack.vpc)
    
    template = assertions.Template.from_stack(application_stack)
    # The test verifies whether the created AWS EC2 instance is of the type 't3.micro'
    template.has_resource_properties("AWS::EC2::Instance", {
        'InstanceType': assertions.Match.string_like_regexp('(t2|t3).micro'),
        'ImageId': assertions.Match.any_value(),  # We can ignore the specific AMI ID since it may vary
        'KeyName': assertions.Match.absent(),  # We can ignore the key name since it may vary
    })
    


def test_web_server_security_group():
    app = core.App()
    
    # Create the root stack to hold the nested stacks.
    root_stack = core.Stack(app, "RootStack")

    # Define the network stack and reference the root stack as its parent. 
    # This stack will create the VPC and related networking resources.
    network_stack = NetworkStack(root_stack, "NetworkStack")

    # Define the application stack and reference the root stack as its parent.
    # This stack will create the application resources, including an EC2 instance that serves a web page.
    application_stack = ApplicationStack(root_stack, "ApplicationStack", main_vpc=network_stack.vpc)
    
    template = assertions.Template.from_stack(application_stack)
    # The test verifies whether the created AWS Security Group allows inbound HTTP traffic on port 80 from anywhere
    template.has_resource_properties("AWS::EC2::SecurityGroup", {
        # `assertions.Match.array_with` is used to check that the 'SecurityGroupIngress' property contains an object
        # with the specified properties, allowing for other ingress rules to be present as well
        'SecurityGroupIngress': assertions.Match.array_with([
            assertions.Match.object_like({
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'CidrIp': '0.0.0.0/0',
                'Description': assertions.Match.any_value(),  # We can ignore the description since it may vary
            })
        ]),
    })