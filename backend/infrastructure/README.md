# ContractGuard Infrastructure (Python CDK)

AWS CDK infrastructure for ContractGuard - AI-powered contract analysis for Indian small businesses.

## Why cdk.json is Required

The `cdk.json` file is **essential** for AWS CDK. It:
- Tells CDK how to execute your app (`"app": "python3 app.py"`)
- Contains feature flags for CDK behavior
- Configures file watching for `cdk watch` command
- Stores context values for your CDK app

**Do not delete this file** - CDK will not work without it.

## Prerequisites

- **Python 3.11+** - Required for CDK and Lambda functions
- **AWS CLI** - Configured with credentials (`aws configure`)
- **AWS CDK CLI** - Install globally: `npm install -g aws-cdk`

## Quick Start

1. **Create virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Bootstrap CDK** (first time only):
   ```bash
   cdk bootstrap aws://ACCOUNT-ID/us-east-1
   ```

4. **Deploy**:
   ```bash
   cdk deploy
   ```

## Project Structure

```
backend/infrastructure/
├── app.py                      # CDK app entry point
├── cdk.json                    # CDK configuration (REQUIRED)
├── requirements.txt            # Python dependencies
├── lib/
│   ├── __init__.py
│   └── contract_guard_stack.py # Stack definition
├── DEPLOYMENT.md               # Detailed deployment guide
└── README.md                   # This file
```

## Useful Commands

| Command | Description |
|---------|-------------|
| `cdk ls` | List all stacks |
| `cdk synth` | Synthesize CloudFormation template |
| `cdk diff` | Compare deployed stack with current state |
| `cdk deploy` | Deploy stack to AWS |
| `cdk deploy -c env=prod` | Deploy to production environment |
| `cdk destroy` | Remove stack from AWS |
| `cdk watch` | Watch for changes and auto-deploy |

## Stack Resources

The ContractGuard stack creates:

### Storage
- **S3 Buckets**: Frontend hosting, contract storage, report storage
- **DynamoDB Tables**: Contracts metadata, analysis results

### Compute
- **Lambda Functions**: Upload handler, analyze processor, report generator
- **API Gateway**: REST API with Cognito authorization

### Security & Auth
- **Cognito User Pool**: User authentication and management
- **IAM Roles**: Least-privilege permissions for Lambda functions

### Networking & Delivery
- **CloudFront Distribution**: Global CDN for frontend

### Monitoring
- **CloudWatch Log Groups**: Lambda function logs (7-day retention)
- **CloudWatch Alarms**: Free Tier usage monitoring (80% thresholds)

## Environment Variables

The stack uses these environment variables:
- `CDK_DEFAULT_ACCOUNT` - AWS account ID (auto-detected)
- `CDK_DEFAULT_REGION` - AWS region (defaults to us-east-1)

Set environment context:
```bash
cdk deploy -c env=dev    # Development (default)
cdk deploy -c env=prod   # Production
```

## AWS Free Tier Compliance

The infrastructure is designed to stay within AWS Free Tier limits:
- **Lambda**: 1M requests/month, 400K GB-seconds compute
- **S3**: 5GB storage, 20K GET, 2K PUT requests/month
- **DynamoDB**: 25GB storage, 25 read/write capacity units
- **API Gateway**: 1M requests/month (first 12 months)
- **CloudFront**: 1TB data transfer, 10M requests/month

CloudWatch alarms monitor usage at 80% thresholds.

## Deployment Outputs

After deployment, CDK outputs these values (save them for frontend configuration):

```
CloudFrontURL          - Frontend application URL
ApiUrl                 - API Gateway endpoint
UserPoolId             - Cognito User Pool ID
UserPoolClientId       - Cognito User Pool Client ID
ContractsBucketName    - S3 bucket for contracts
ReportsBucketName      - S3 bucket for reports
```

## Troubleshooting

### "CDK bootstrap stack not found"
```bash
cdk bootstrap aws://YOUR-ACCOUNT-ID/us-east-1 --force
```

### "No module named 'aws_cdk'"
```bash
pip install -r requirements.txt
```

### Lambda deployment fails
Ensure Lambda code directories exist:
- `backend/lambda/upload/`
- `backend/lambda/analyze/`
- `backend/lambda/report/`

### Permission errors
Ensure AWS credentials have permissions for:
CloudFormation, S3, Lambda, DynamoDB, Cognito, API Gateway, CloudFront, IAM

## Development Workflow

1. Make changes to `lib/contract_guard_stack.py`
2. Review changes: `cdk diff`
3. Deploy changes: `cdk deploy`
4. Monitor logs: `aws logs tail /aws/lambda/contract-guard-analyze-dev --follow`

## Additional Resources

- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [CDK Workshop](https://cdkworkshop.com/30-python.html)
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detailed deployment guide

## Notes

- All Lambda functions use Python 3.11 runtime
- Infrastructure uses Python CDK (not TypeScript)
- Frontend remains TypeScript/React
- Stack is designed for us-east-1 region (AWS Free Tier)
