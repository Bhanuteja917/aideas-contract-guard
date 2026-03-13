# ContractGuard

AI-powered contract analysis tool for Indian small businesses, freelancers, and solopreneurs.

## Overview

ContractGuard democratizes legal protection by analyzing contracts for hidden risks, unfair clauses, and compliance issues, providing plain-language explanations and risk scores without expensive legal fees.

## Features

- 📄 PDF contract upload with drag-and-drop
- 🤖 AI-powered analysis using Amazon Bedrock (Claude)
- 📊 Risk scoring across 4 categories (Financial, Legal, IP, Termination)
- 🌐 Bilingual explanations (English & Hindi)
- ⚖️ Indian Contract Law compliance checking
- 📈 Visual risk dashboard
- 📑 Downloadable PDF reports

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Recharts for visualizations
- Amazon Cognito Identity SDK for authentication

### Backend (100% Python)
- **Infrastructure**: AWS CDK (Python)
- **Lambda Functions**: Python 3.11
- **AI Services**:
  - Amazon Bedrock (Claude model) - Clause analysis
  - Amazon Textract - PDF text extraction (fallback)
  - Amazon Comprehend - Entity detection
- **Storage**:
  - Amazon S3 - File storage (contracts, reports, frontend)
  - Amazon DynamoDB - Metadata and analysis results
- **Security & API**:
  - Amazon Cognito - User authentication
  - API Gateway - REST API with Cognito authorizer
  - CloudFront - CDN for frontend delivery

## Project Structure

```
contractguard/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── contexts/     # Auth context
│   │   ├── services/     # API services
│   │   └── utils/        # Utility functions
│   └── package.json
├── backend/
│   ├── lambda/           # Python Lambda functions
│   │   ├── upload/       # Upload handler (Python 3.11)
│   │   ├── analyze/      # Analysis pipeline (Python 3.11)
│   │   └── report/       # Report generator (Python 3.11)
│   └── infrastructure/   # Python CDK infrastructure
│       ├── app.py        # CDK app entry point
│       ├── lib/          # Stack definitions
│       └── requirements.txt
└── .kiro/specs/          # Feature specifications
```

## Getting Started

### Prerequisites

- **Frontend**: Node.js 18+ and npm 9+
- **Backend**: Python 3.11+
- **AWS**: Account with Free Tier, AWS CLI configured
- **CDK**: AWS CDK CLI (`npm install -g aws-cdk`)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd contractguard
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install infrastructure dependencies:
```bash
cd backend/infrastructure
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4. Configure AWS credentials:
```bash
aws configure
```

### Deployment

1. **Deploy infrastructure** (from `backend/infrastructure`):
```bash
cdk bootstrap  # First time only
cdk deploy
```

2. **Configure frontend** with deployment outputs in `frontend/.env.local`:
```env
VITE_USER_POOL_ID=<UserPoolId from CDK output>
VITE_USER_POOL_CLIENT_ID=<UserPoolClientId from CDK output>
VITE_API_URL=<ApiUrl from CDK output>
VITE_AWS_REGION=us-east-1
```

3. **Build and deploy frontend**:
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://<FrontendBucketName> --delete
```

### Development

Start the frontend development server:
```bash
cd frontend
npm run dev
```

View Lambda logs:
```bash
aws logs tail /aws/lambda/contract-guard-analyze-dev --follow
```

## AWS Free Tier Compliance

This project is designed to operate within AWS Free Tier limits:

- **Amazon Bedrock**: Limited free tier for Claude model
- **Amazon Textract**: 1,000 pages/month for first 3 months
- **Amazon Comprehend**: 50,000 units/month for first 12 months
- **Amazon S3**: 5GB storage, 20,000 GET, 2,000 PUT requests/month
- **AWS Lambda**: 1M requests/month, 400,000 GB-seconds compute
- **Amazon Cognito**: 50,000 MAUs
- **API Gateway**: 1M API calls/month for first 12 months

## Competition

Built for the **AWS 10,000 AIdeas Competition** (Social Impact Category)

- **Deadline**: March 13, 2026, 4:00 AM IST
- **Category**: #social-impact
- **Region**: #APJC (Asia Pacific Japan China)

## License

MIT License - see LICENSE file for details

## Acknowledgments

- AWS 10,000 AIdeas Competition
- Kiro IDE for development assistance
- Indian small business community
