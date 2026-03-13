# ContractGuard Deployment Guide

This guide covers deploying the ContractGuard infrastructure using AWS CDK (Python).

## Prerequisites

1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS CLI**: Installed and configured with credentials
   ```bash
   aws configure
   ```
3. **Python 3.11+**: Required for CDK and Lambda functions
4. **AWS CDK CLI**: Install globally
   ```bash
   npm install -g aws-cdk
   ```

## Initial Setup

### 1. Install Python Dependencies

Navigate to the infrastructure directory:
```bash
cd backend/infrastructure
```

Create and activate a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install CDK dependencies:
```bash
pip install -r requirements.txt
```

### 2. Bootstrap CDK (First Time Only)

Bootstrap your AWS account for CDK:
```bash
cdk bootstrap aws://YOUR-ACCOUNT-ID/us-east-1
```

Replace `YOUR-ACCOUNT-ID` with your AWS account ID. You can find it by running:
```bash
aws sts get-caller-identity --query Account --output text
```

## Deployment

### Deploy to Development Environment

From the `backend/infrastructure` directory:

```bash
cdk deploy
```

This deploys to the `dev` environment by default.

### Deploy to Production Environment

```bash
cdk deploy -c env=prod
```

### View Changes Before Deploying

```bash
cdk diff
```

### Synthesize CloudFormation Template

```bash
cdk synth
```

## Post-Deployment

After successful deployment, CDK will output important values:

```
Outputs:
ContractGuardStack-dev.CloudFrontURL = https://d3cel0medhyrga.cloudfront.net
ContractGuardStack-dev.ApiUrl = https://eb4ol1vz96.execute-api.us-east-1.amazonaws.com/dev/
ContractGuardStack-dev.UserPoolId = us-east-1_6tXoldSiC
ContractGuardStack-dev.UserPoolClientId = 3r8ostuelf0470s14be5u9go45
...
```

### Configure Frontend

Update `frontend/.env.local` with the deployment outputs:

```env
VITE_USER_POOL_ID=us-east-1_6tXoldSiC
VITE_USER_POOL_CLIENT_ID=3r8ostuelf0470s14be5u9go45
VITE_API_URL=https://eb4ol1vz96.execute-api.us-east-1.amazonaws.com/dev
VITE_AWS_REGION=us-east-1
```

### Deploy Frontend to S3

From the `frontend` directory:

```bash
# Build the frontend
npm run build

# Upload to S3 (replace bucket name with your FrontendBucketName output)
aws s3 sync dist/ s3://contract-guard-frontend-dev-882334376986 --delete

# Invalidate CloudFront cache (replace distribution ID with your CloudFrontDistributionId output)
aws cloudfront create-invalidation --distribution-id E1234567890ABC --paths "/*"
```

## Verification

1. **Check Stack Status**:
   ```bash
   aws cloudformation describe-stacks --stack-name contract-guard-dev
   ```

2. **Test API Gateway**:
   ```bash
   curl https://YOUR-API-URL/dev/contracts/upload
   # Should return 401 Unauthorized (expected without auth)
   ```

3. **Access Frontend**:
   Open the CloudFront URL in your browser

## Updating the Stack

After making changes to the infrastructure code:

```bash
# View changes
cdk diff

# Deploy changes
cdk deploy
```

## Destroying the Stack

To remove all resources:

```bash
cdk destroy
```

**Warning**: This will delete all data including uploaded contracts and analyses.

## Troubleshooting

### CDK Bootstrap Issues

If you see "CDK bootstrap stack not found":
```bash
cdk bootstrap aws://YOUR-ACCOUNT-ID/us-east-1 --force
```

### Lambda Deployment Issues

If Lambda functions fail to deploy, ensure the Lambda code directories exist:
- `backend/lambda/upload/`
- `backend/lambda/analyze/`
- `backend/lambda/report/`

### Permission Errors

Ensure your AWS credentials have sufficient permissions:
- CloudFormation
- S3
- Lambda
- DynamoDB
- Cognito
- API Gateway
- CloudFront
- IAM

## Monitoring

### CloudWatch Logs

View Lambda logs:
```bash
aws logs tail /aws/lambda/contract-guard-upload-dev --follow
aws logs tail /aws/lambda/contract-guard-analyze-dev --follow
aws logs tail /aws/lambda/contract-guard-report-dev --follow
```

### CloudWatch Alarms

The stack creates alarms for Free Tier monitoring:
- Lambda invocations (800K/month threshold)
- S3 storage (4GB threshold)
- API Gateway requests (800K/month threshold)

View alarms:
```bash
aws cloudwatch describe-alarms --alarm-name-prefix contract-guard
```

## Cost Management

The infrastructure is designed to stay within AWS Free Tier limits:
- Lambda: 1M requests/month, 400K GB-seconds
- S3: 5GB storage, 20K GET, 2K PUT requests/month
- DynamoDB: 25GB storage, 25 read/write capacity units
- API Gateway: 1M requests/month (first 12 months)
- CloudFront: 1TB data transfer out, 10M requests/month

Monitor usage in AWS Cost Explorer and CloudWatch.

## Support

For issues or questions:
1. Check CloudWatch logs for error messages
2. Review AWS CloudFormation events for deployment issues
3. Verify all prerequisites are met
4. Ensure AWS credentials are properly configured
