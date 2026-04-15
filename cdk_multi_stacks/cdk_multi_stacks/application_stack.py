from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
    aws_s3_assets as s3_assets,
)
from constructs import Construct


# This stack defines the application resources, including an EC2 instance that serves a web page.
# It takes a VPC reference from the network stack to deploy the EC2 instance within that VPC.
class ApplicationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, main_vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


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
            "rm -rf /usr/share/nginx/html/*",
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

        # Output the public DNS name of the EC2 instance.
        CfnOutput(
            self,
            "WebServerPublicDNS",
            value=web_server.instance_public_dns_name,
            description="The public DNS name of the web server instance",
        )

        # Deploying a local file to the EC2 instance using S3 assets.
        web_page_asset = s3_assets.Asset(self, "WebPageAsset", path="../cdk_s3_assets/web_pages/index.html")
        
        # Add a command to the EC2 instance's user data to download the file from S3 and place it in the NGINX web root directory.
        web_server.user_data.add_s3_download_command(
            bucket=web_page_asset.bucket,
            bucket_key=web_page_asset.s3_object_key,
            local_file="/usr/share/nginx/html/index.html"
        )
        
        # Grant read permissions on the S3 asset to the EC2 instance's role.
        web_page_asset.grant_read(web_server.role)
        
        # Start the NGINX service on the EC2 instance.
        web_server.add_user_data(
            "sudo systemctl start nginx",
        )