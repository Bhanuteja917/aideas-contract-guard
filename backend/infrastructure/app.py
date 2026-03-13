#!/usr/bin/env python3
import os
import aws_cdk as cdk
from lib.contract_guard_stack import ContractGuardStack

app = cdk.App()

env_name = app.node.try_get_context("env") or "dev"

ContractGuardStack(
    app,
    f"ContractGuardStack-{env_name}",
    stack_name=f"contract-guard-{env_name}",
    description="ContractGuard - AI-powered contract analysis for Indian small businesses",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
    ),
    tags={
        "Project": "ContractGuard",
        "Environment": env_name,
        "ManagedBy": "CDK",
    },
)

app.synth()
