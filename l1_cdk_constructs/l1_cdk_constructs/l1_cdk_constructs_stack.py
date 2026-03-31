# This is a CDK Stack that defines a VPC with 2 public and 2 private subnets and
# routing configurations using L1 constructs.
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class L1CdkConstructsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with default settings
        vpc = ec2.CfnVPC(self, "Main_VPC",
                          cidr_block="10.0.0.0/16",
                          enable_dns_support=True,
                          enable_dns_hostnames=True)
        
        internet_gateway = ec2.CfnInternetGateway(self, "InternetGateway_Main_VPC")
        
        ec2.CfnVPCGatewayAttachment(self, "IGwAttachment_Main_VPC",
                                      vpc_id=vpc.attr_vpc_id,
                                      internet_gateway_id=internet_gateway.attr_internet_gateway_id)
        
        # Define subnets with specific CIDR blocks and public/private settings
        main_vpc_subnets = [
            {"cidr_block": "10.0.0.0/24", "public": True},
            {"cidr_block": "10.0.1.0/24", "public": True},
            {"cidr_block": "10.0.2.0/24", "public": False},
            {"cidr_block": "10.0.3.0/24", "public": False}
        ]
        
        # Create subnets based on the defined settings and associate them with the VPC.
        # Additionally, create route tables for each subnet and associate them with the appropriate subnets.
        for index, subnet in enumerate(main_vpc_subnets):
            subnet_resource = ec2.CfnSubnet(self, f"Subnet{index+1}",
                                             vpc_id=vpc.attr_vpc_id,
                                             cidr_block=subnet["cidr_block"],
                                             map_public_ip_on_launch=subnet["public"],
                                             availability_zone=Stack.availability_zones.fget(self)[index % 2])
        
            route_table = ec2.CfnRouteTable(self, f"Subnet{index+1}RouteTable",
                                                  vpc_id=vpc.attr_vpc_id)
            
            # Associate the route table with the subnet
            ec2.CfnSubnetRouteTableAssociation(self, f"Subnet{index+1}RouteTableAssociation",
                                              subnet_id=subnet_resource.attr_subnet_id,
                                              route_table_id=route_table.attr_route_table_id)
            
            # If the subnet is public, add a route to the Internet Gateway
            if subnet["public"]:
                ec2.CfnRoute(self, f"Subnet{index+1}InternetRoute",
                             route_table_id=route_table.attr_route_table_id,
                             destination_cidr_block="0.0.0.0/0",
                             gateway_id=internet_gateway.attr_internet_gateway_id)
                
                
                