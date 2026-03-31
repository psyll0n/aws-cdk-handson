from aws_cdk import (
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct

class L2CdkConstructsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_primary = ec2.Vpc(self, "VPCPrimary",
                              nat_gateways=0,
                              max_azs=3
        )