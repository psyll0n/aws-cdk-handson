#!/usr/bin/env python3

import aws_cdk as cdk

from starter_cdk_app.starter_cdk_app_stack import StarterCdkAppStack


app = cdk.App()
StarterCdkAppStack(app, "StarterCdkAppStack")

app.synth()
