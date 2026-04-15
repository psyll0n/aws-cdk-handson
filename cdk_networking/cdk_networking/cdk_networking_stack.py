from aws_cdk import CfnOutput, RemovalPolicy, Stack, aws_ec2 as ec2, aws_rds as rds
from constructs import Construct


class CdkNetworkingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with no NAT gateways.
        main_vpc = ec2.Vpc(self, "MainVPC", nat_gateways=0)

        # Create a public EC2 instance in the VPC.
        web_server = ec2.Instance(
            self,
            "WebServer",
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            vpc=main_vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            user_data_causes_replacement=True,
        )

        # Attach an Elastic IP to the EC2 instance.
        ec2.CfnEIP(self, "WebServerEIP", instance_id=web_server.instance_id)

        # Installing NGINX on the EC2 instance using user data.
        web_server.user_data.add_commands(
            "sudo dnf update -y",
            "sudo dnf install nginx -y",
            "sudo systemctl start nginx",
            "sudo systemctl enable nginx",
        )

        # Allow inbound HTTP traffic on port 80 from anywhere.
        web_server.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), "Allow inbound HTTP traffic from anywhere"
        )

        # Allow inbound SSH traffic on port 22 from anywhere.
        web_server.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22), "Allow inbound SSH traffic from anywhere"
        )

        # Output the public IP address of the EC2 instance.
        CfnOutput(
            self,
            "WebServerPublicIP",
            value=web_server.instance_public_ip,
            description="The public IP address of the web server instance",
        )

        CfnOutput(
            self,
            "WebServerPublicDNS",
            value=web_server.instance_public_dns_name,
            description="The public DNS name of the web server instance",
        )

        # PostgreSQL Database instance configuration
        db_instance = rds.DatabaseInstance(
            self,
            "DbInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            vpc=main_vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            multi_az=False,
            allocated_storage=20,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Allow the EC2 instance to connect to the RDS instance on the default PostgreSQL port (5432).
        db_instance.connections.allow_from(
            web_server,
            ec2.Port.tcp(5432),
            "Allow EC2 instance to connect to RDS instance on port 5432",
        )

        # Alternatively, you can use the line below to enable access from the web server's security group to the RDS instance.
        # db_instance.connections.allow_default_port_from(web_server,
        #                                                 "Allow EC2 instance to connect to RDS instance on default PostgreSQL port")

        # Installing MySQL client on the EC2 instance using user data.
        web_server.user_data.add_commands("sudo dnf install mysql -y")

        # Output the RDS instance endpoint address and credentials.
        CfnOutput(
            self,
            "DbInstanceEndpoint",
            value=db_instance.db_instance_endpoint_address,
            description="The endpoint address of the RDS instance",
        )
