from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_s3_notifications as s3n,
    aws_apigateway as apigateway,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class ContractGuardStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = self.node.try_get_context("env") or "dev"

        # S3 Buckets

        # Frontend bucket for static website hosting
        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=f"contract-guard-frontend-{env_name}-{self.account}",
            website_index_document="index.html",
            website_error_document="index.html",  # SPA routing
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                )
            ],
        )

        # Contracts bucket for uploaded PDFs
        contracts_bucket = s3.Bucket(
            self,
            "ContractsBucket",
            bucket_name=f"contract-guard-contracts-{env_name}-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldContracts",
                    enabled=True,
                    expiration=Duration.days(30),  # Auto-cleanup after 30 days
                )
            ],
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.POST],
                    allowed_origins=["*"],  # Will be restricted to CloudFront domain later
                    allowed_headers=["*"],
                    exposed_headers=["ETag"],
                )
            ],
        )

        # Reports bucket for generated PDFs
        reports_bucket = s3.Bucket(
            self,
            "ReportsBucket",
            bucket_name=f"contract-guard-reports-{env_name}-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldReports",
                    enabled=True,
                    expiration=Duration.days(7),  # Reports expire after 7 days
                )
            ],
        )

        # CloudFront Distribution for frontend
        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(frontend_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
                compress=True,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5),
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5),
                ),
            ],
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # Use only North America and Europe
            comment=f"ContractGuard Frontend Distribution - {env_name}",
        )

        # Cognito User Pool for authentication
        user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=f"contract-guard-users-{env_name}",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY,
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True)
            ),
        )

        # User Pool Client for web app
        user_pool_client = user_pool.add_client(
            "WebClient",
            user_pool_client_name=f"contract-guard-web-client-{env_name}",
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True),
            generate_secret=False,  # Public client (browser-based)
            prevent_user_existence_errors=True,
            refresh_token_validity=Duration.days(30),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
        )

        # DynamoDB Tables

        # Contracts table
        contracts_table = dynamodb.Table(
            self,
            "ContractsTable",
            table_name=f"ContractGuard-Contracts-{env_name}",
            partition_key=dynamodb.Attribute(
                name="contractId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # On-demand pricing for Free Tier
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=False,  # Disabled to stay in Free Tier
        )

        # GSI for querying contracts by user
        contracts_table.add_global_secondary_index(
            index_name="userId-uploadedAt-index",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="uploadedAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # Analyses table
        analyses_table = dynamodb.Table(
            self,
            "AnalysesTable",
            table_name=f"ContractGuard-Analyses-{env_name}",
            partition_key=dynamodb.Attribute(
                name="analysisId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=False,
        )

        # GSI for querying analyses by contract
        analyses_table.add_global_secondary_index(
            index_name="contractId-index",
            partition_key=dynamodb.Attribute(
                name="contractId", type=dynamodb.AttributeType.STRING
            ),
        )

        # Lambda Functions

        # Upload Lambda (Python)
        upload_lambda = PythonFunction(
            self,
            "UploadLambda",
            function_name=f"contract-guard-upload-{env_name}",
            entry="../lambda/upload",
            runtime=lambda_.Runtime.PYTHON_3_11,
            index="lambda_function.py",
            handler="lambda_handler",
            environment={
                "CONTRACTS_BUCKET": contracts_bucket.bucket_name,
                "CONTRACTS_TABLE": contracts_table.table_name,
                "USER_POOL_ID": user_pool.user_pool_id,
                "ANALYSES_TABLE": analyses_table.table_name,
            },
            timeout=Duration.seconds(30),
            memory_size=256,
        )

        # Grant permissions to upload Lambda
        contracts_bucket.grant_read_write(upload_lambda)
        contracts_table.grant_read_write_data(upload_lambda)
        analyses_table.grant_read_data(upload_lambda)

        # Analyze Lambda (Python)
        analyze_lambda = PythonFunction(
            self,
            "AnalyzeLambda",
            function_name=f"contract-guard-analyze-{env_name}",
            entry="../lambda/analyze",
            runtime=lambda_.Runtime.PYTHON_3_11,
            index="lambda_function.py",
            handler="lambda_handler",
            environment={
                "CONTRACTS_BUCKET": contracts_bucket.bucket_name,
                "CONTRACTS_TABLE": contracts_table.table_name,
                "ANALYSES_TABLE": analyses_table.table_name,
            },
            timeout=Duration.minutes(5),  # AI processing can take time
            memory_size=1024,
        )

        # Grant permissions to analyze Lambda
        contracts_bucket.grant_read(analyze_lambda)
        contracts_table.grant_read_write_data(analyze_lambda)
        analyses_table.grant_read_write_data(analyze_lambda)

        # Grant AI service permissions
        analyze_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "textract:DetectDocumentText",
                    "comprehend:DetectEntities",
                    "bedrock:InvokeModel",
                ],
                resources=["*"],
            )
        )
        
        # Grant AWS Marketplace permissions for Bedrock models
        analyze_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "aws-marketplace:ViewSubscriptions",
                    "aws-marketplace:Subscribe",
                ],
                resources=["*"],
            )
        )

        # S3 trigger for analyze Lambda
        contracts_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(analyze_lambda),
            s3.NotificationKeyFilter(suffix=".pdf"),
        )

        # Report Lambda (Python)
        report_lambda = PythonFunction(
            self,
            "ReportLambda",
            function_name=f"contract-guard-report-{env_name}",
            entry="../lambda/report",
            runtime=lambda_.Runtime.PYTHON_3_11,
            index="lambda_function.py",
            handler="lambda_handler",
            environment={
                "ANALYSES_TABLE": analyses_table.table_name,
                "REPORTS_BUCKET": reports_bucket.bucket_name,
            },
            timeout=Duration.seconds(30),
            memory_size=512,
        )

        # Grant permissions to report Lambda
        analyses_table.grant_read_data(report_lambda)
        reports_bucket.grant_read_write(report_lambda)

        # API Gateway
        api = apigateway.RestApi(
            self,
            "ContractGuardAPI",
            rest_api_name=f"contract-guard-api-{env_name}",
            description="ContractGuard API for contract analysis",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,  # Will be restricted to CloudFront later
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
                allow_credentials=True,
            ),
            deploy_options=apigateway.StageOptions(
                stage_name=env_name,
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
        )

        # Cognito Authorizer
        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
            authorizer_name=f"contract-guard-authorizer-{env_name}",
            identity_source="method.request.header.Authorization",
        )

        # API Resources and Methods

        # /contracts resource
        contracts = api.root.add_resource("contracts")
        
        # GET /contracts - list all contracts for user
        contracts.add_method(
            "GET",
            apigateway.LambdaIntegration(upload_lambda),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )
        
        # POST /contracts/upload
        upload = contracts.add_resource("upload")
        upload.add_method(
            "POST",
            apigateway.LambdaIntegration(upload_lambda),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )

        # GET /contracts/{contractId}
        contract = contracts.add_resource("{contractId}")
        contract.add_method(
            "GET",
            apigateway.LambdaIntegration(upload_lambda),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )

        # GET /contracts/{contractId}/report
        report = contract.add_resource("report")
        report.add_method(
            "GET",
            apigateway.LambdaIntegration(report_lambda),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )

        # CloudWatch Log Groups (Lambda functions automatically create log groups, but we define retention)
        logs.LogGroup(
            self,
            "UploadLambdaLogGroup",
            log_group_name=f"/aws/lambda/{upload_lambda.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        logs.LogGroup(
            self,
            "AnalyzeLambdaLogGroup",
            log_group_name=f"/aws/lambda/{analyze_lambda.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        logs.LogGroup(
            self,
            "ReportLambdaLogGroup",
            log_group_name=f"/aws/lambda/{report_lambda.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # CloudWatch Alarms for Free Tier monitoring

        # Lambda invocations alarm (80% of 1M free tier)
        cloudwatch.Alarm(
            self,
            "LambdaInvocationsAlarm",
            alarm_name=f"contract-guard-lambda-invocations-{env_name}",
            alarm_description="Alert when Lambda invocations exceed 80% of Free Tier (800K)",
            metric=cloudwatch.Metric(
                namespace="AWS/Lambda",
                metric_name="Invocations",
                statistic="Sum",
                period=Duration.days(1),
            ),
            threshold=800000,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        )

        # S3 storage alarm (80% of 5GB free tier)
        cloudwatch.Alarm(
            self,
            "S3StorageAlarm",
            alarm_name=f"contract-guard-s3-storage-{env_name}",
            alarm_description="Alert when S3 storage exceeds 80% of Free Tier (4GB)",
            metric=cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="BucketSizeBytes",
                statistic="Average",
                period=Duration.days(1),
                dimensions_map={
                    "BucketName": contracts_bucket.bucket_name,
                    "StorageType": "StandardStorage",
                },
            ),
            threshold=4 * 1024 * 1024 * 1024,  # 4GB in bytes
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        )

        # API Gateway requests alarm (80% of 1M free tier)
        cloudwatch.Alarm(
            self,
            "ApiRequestsAlarm",
            alarm_name=f"contract-guard-api-requests-{env_name}",
            alarm_description="Alert when API requests exceed 80% of Free Tier (800K)",
            metric=api.metric_count(period=Duration.days(1), statistic="Sum"),
            threshold=800000,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        )

        # Outputs
        CfnOutput(
            self,
            "FrontendBucketName",
            value=frontend_bucket.bucket_name,
            description="Frontend S3 bucket name",
        )

        CfnOutput(
            self,
            "ContractsBucketName",
            value=contracts_bucket.bucket_name,
            description="Contracts S3 bucket name",
        )

        CfnOutput(
            self,
            "ReportsBucketName",
            value=reports_bucket.bucket_name,
            description="Reports S3 bucket name",
        )

        CfnOutput(
            self,
            "CloudFrontURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="CloudFront distribution URL",
        )

        CfnOutput(
            self,
            "CloudFrontDistributionId",
            value=distribution.distribution_id,
            description="CloudFront distribution ID",
        )

        CfnOutput(
            self,
            "UserPoolId",
            value=user_pool.user_pool_id,
            description="Cognito User Pool ID",
        )

        CfnOutput(
            self,
            "UserPoolClientId",
            value=user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID",
        )

        CfnOutput(
            self,
            "ContractsTableName",
            value=contracts_table.table_name,
            description="Contracts DynamoDB table name",
        )

        CfnOutput(
            self,
            "AnalysesTableName",
            value=analyses_table.table_name,
            description="Analyses DynamoDB table name",
        )

        CfnOutput(
            self, "ApiUrl", value=api.url, description="API Gateway URL"
        )

        CfnOutput(
            self,
            "ApiId",
            value=api.rest_api_id,
            description="API Gateway ID",
        )

        CfnOutput(
            self,
            "Environment",
            value=env_name,
            description="Deployment environment",
        )
