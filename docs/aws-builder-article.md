# Building ContractGuard: AI-Powered Legal Protection for Everyone

## The Problem: Millions Sign Contracts They Don't Understand

Every year, millions of Indians sign contracts without fully understanding what they're agreeing to. A freelancer in Pune signs a service agreement with a one-sided IP clause that transfers all creative work to the client. A young professional in Bengaluru signs a lease with an auto-renewal clause that locks them in for another year. A small business owner in Delhi signs a vendor agreement with penalty clauses that cost them lakhs when things go wrong.

The problem isn't carelessness—it's accessibility. Legal review is expensive (₹5,000 to ₹25,000 per consultation), slow, and simply not viable for most people reviewing everyday contracts.

**ContractGuard** is my solution: an AI-powered contract analysis platform that reads any contract and provides a clear, plain-English breakdown of risks, missing protections, and negotiation points—in seconds, for free.

**Try the live app:** https://d3cel0medhyrga.cloudfront.net/

## Why This Matters

India has over 63 million small businesses, 15 million freelancers, and hundreds of millions of salaried individuals who regularly sign contracts. Yet legal literacy remains extremely low. Most people sign rental agreements, employment contracts, NDAs, and vendor contracts without understanding the implications.

ContractGuard eliminates the cost barrier entirely, giving anyone with a smartphone the ability to understand what they're signing.

## Architecture: Serverless on AWS Free Tier

I built ContractGuard entirely on AWS Free Tier using a serverless, event-driven architecture. Here's how it works:

### Core Components

- **Amazon S3**: Three buckets for frontend hosting, contract storage, and generated reports
- **Amazon CloudFront**: CDN for fast global frontend delivery with HTTPS
- **Amazon Cognito**: User authentication and authorization
- **AWS Lambda**: Three Python functions for upload orchestration, AI analysis, and report generation
- **Amazon Bedrock (Nova Pro)**: AI-powered contract risk analysis
- **Amazon Textract**: OCR fallback for scanned PDFs
- **Amazon Comprehend**: Entity extraction (parties, dates, amounts)
- **Amazon DynamoDB**: Two tables for contract metadata and analysis results
- **Amazon API Gateway**: REST API with Cognito authorizer
- **Amazon CloudWatch**: Free Tier usage monitoring and alarms

### Event-Driven Analysis Pipeline

1. User authenticates via Cognito and requests pre-signed S3 upload URL
2. Frontend uploads PDF directly to S3 (bypassing API Gateway for large files)
3. S3 triggers the Analyze Lambda automatically on object creation
4. Lambda extracts text using PyPDF2 (with Textract fallback for scanned docs)
5. Comprehend identifies entities (parties, dates, monetary amounts)
6. Bedrock (Nova Pro) analyzes clauses, calculates risk scores, and generates explanations
7. Results stored in DynamoDB with GSI for fast user queries
8. Frontend polls for analysis completion and displays color-coded dashboard
9. Optional: User requests PDF report via Report Lambda

### Infrastructure as Code with AWS CDK

I used AWS CDK (Python) to define all infrastructure, making the entire stack reproducible and version-controlled. This approach made it easy to iterate on the architecture and deploy updates confidently.

```python
# S3 bucket with automatic cleanup to stay in Free Tier
contracts_bucket = s3.Bucket(
    self, "ContractsBucket",
    encryption=s3.BucketEncryption.S3_MANAGED,
    block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
    lifecycle_rules=[
        s3.LifecycleRule(
            id="DeleteOldContracts",
            enabled=True,
            expiration=Duration.days(30)  # Auto-cleanup after 30 days
        )
    ]
)

# S3 event trigger for automatic analysis
contracts_bucket.add_event_notification(
    s3.EventType.OBJECT_CREATED,
    s3n.LambdaDestination(analyze_lambda),
    s3.NotificationKeyFilter(suffix=".pdf")
)

# CloudWatch alarm to monitor Free Tier usage
cloudwatch.Alarm(
    self, "LambdaInvocationsAlarm",
    alarm_description="Alert when Lambda invocations exceed 80% of Free Tier (800K)",
    metric=cloudwatch.Metric(
        namespace="AWS/Lambda",
        metric_name="Invocations",
        statistic="Sum",
        period=Duration.days(1)
    ),
    threshold=800000,
    evaluation_periods=1
)
```

## What the App Delivers

When you upload a contract to ContractGuard, you get:

- **Overall risk score**: 1-10 scale with weighted category analysis (financial, legal liability, IP, termination)
- **Clause-by-clause breakdown**: Plain-English and Hindi explanations of risky clauses
- **Entity extraction**: Automatic identification of parties, dates, amounts, and key terms
- **Red flags**: Unfair or one-sided clauses highlighted with risk scores
- **Indian Contract Act compliance**: Checks for violations of Sections 23, 27, 28, and jurisdiction issues
- **Negotiation recommendations**: Specific alternative language and fallback positions for high-risk clauses (score ≥7)
- **Downloadable PDF report**: Complete analysis with all findings and recommendations

## Key Lessons Learned

### 1. Spec-Driven Development with AI

I built ContractGuard using Kiro, an AI-powered IDE. By defining my product vision, technical stack, and architecture in structured specification files upfront, I gave the AI assistant full context throughout development. This dramatically reduced back-and-forth and maintained consistency across sessions.

### 2. Prompt Engineering is Critical

The quality of contract analysis depends entirely on prompt design. My initial prompts returned inconsistent JSON. I learned to:

- Be extremely specific about output structure with JSON schemas
- Provide context about Indian contract law and the Indian Contract Act, 1872
- Calibrate risk scoring with concrete examples (1-10 scale with category weights)
- Use few-shot examples for edge cases
- Request bilingual explanations (English and Hindi) for accessibility
- Separate concerns: one prompt for clause identification, another for explanations, another for compliance

**Example prompt structure:**
```python
prompt = f"""You are an expert contract analyst specializing in identifying risks 
for small businesses in India. Analyze the following contract and identify risky clauses.

ANALYSIS INSTRUCTIONS:
1. Identify all risky clauses in the contract
2. For each risky clause, provide:
   - The clause text (brief excerpt)
   - Risk category (financial, legal_liability, intellectual_property, or termination)
   - Risk score (1-10, where 10 is highest risk)
   - Brief explanation of the risk

3. Focus on these risk patterns:
   - Unfair liability clauses (one-sided indemnification, unlimited liability)
   - Hidden fees or unclear payment terms
   - Restrictive termination clauses (long notice periods, penalties)
   ...

RESPONSE FORMAT (JSON):
{{
  "clauses": [
    {{
      "text": "excerpt of risky clause",
      "category": "financial|legal_liability|intellectual_property|termination",
      "risk_score": 1-10,
      "concern": "brief explanation of risk"
    }}
  ]
}}

Provide ONLY the JSON response, no additional text."""
```

### 3. Cost Optimization from Day One

Amazon Bedrock pricing can add up quickly. I optimized costs by:

- Using Amazon Nova Pro instead of Claude Sonnet (better price-performance for structured analysis)
- Setting strict token limits (4000 for analysis, 500 for explanations, 600 for recommendations)
- Implementing exponential backoff retry logic to avoid duplicate API calls
- Chunking large contracts intelligently to stay within Comprehend's 5000-byte limit
- Using PyPDF2 for text extraction (free) with Textract as fallback only for scanned docs
- Leveraging S3 lifecycle policies to auto-delete contracts after 30 days and reports after 7 days
- Setting CloudWatch alarms at 80% of Free Tier limits (Lambda invocations, S3 storage, API requests)
- Using DynamoDB on-demand pricing to avoid paying for unused capacity

**Free Tier monitoring example:**
```python
cloudwatch.Alarm(
    self, "ApiRequestsAlarm",
    alarm_description="Alert when API requests exceed 80% of Free Tier (800K)",
    metric=api.metric_count(period=Duration.days(1), statistic="Sum"),
    threshold=800000,
    evaluation_periods=1
)
```

### 4. Security and Privacy Matter

Since ContractGuard handles sensitive legal documents, I implemented:

- Pre-signed S3 URLs with 15-minute expiration for uploads and downloads
- Automatic document deletion after 30 days (contracts) and 7 days (reports)
- Cognito user authentication with JWT tokens
- API Gateway Cognito authorizer for all protected endpoints
- User-based access control (users can only access their own contracts)
- S3 bucket encryption (AWS-managed keys)
- DynamoDB encryption at rest
- CloudFront HTTPS-only with redirect from HTTP
- No permanent storage of contract text (only analysis results)

## Technical Challenges and Solutions

### Challenge: PDF Text Extraction Quality

**Problem**: Early versions struggled with scanned PDFs and complex layouts. PyPDF2 returned empty text for image-based PDFs.

**Solution**: I implemented a two-tier extraction pipeline:
1. Try PyPDF2 first (fast, free, works for 90% of PDFs)
2. If PyPDF2 returns empty text, fall back to Amazon Textract (OCR for scanned documents)
3. Add exponential backoff retry logic for Textract rate limits
4. Validate extraction quality and prompt users to upload better quality documents if needed

```python
def extract_text_from_pdf(bucket, key):
    # Try PyPDF2 first
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = "".join(page.extract_text() for page in pdf_reader.pages)
    
    if text.strip():
        return text  # Success with PyPDF2
    
    # Fallback to Textract for scanned documents
    return extract_text_with_textract(bucket, key)
```

### Challenge: Inconsistent AI Responses

**Problem**: Bedrock sometimes returned incomplete or malformed JSON, breaking the analysis pipeline.

**Solution**: I added robust response validation and error handling:
- Parse JSON with try-catch and extract from markdown code blocks
- Validate required fields and provide defaults for missing data
- Implement retry logic with exponential backoff for API failures
- Return partial results rather than failing completely
- Log raw responses for debugging

### Challenge: Comprehend 5000-Byte Limit

**Problem**: Amazon Comprehend has a 5000-byte limit per request, but contracts are often 50KB+.

**Solution**: I implemented intelligent text chunking:
- Split text at sentence boundaries to preserve context
- Track byte offsets to adjust entity positions in original text
- Process chunks sequentially and merge results
- Filter entities to only relevant types (PERSON, DATE, ORGANIZATION, etc.)

### Challenge: Lambda Cold Starts

**Problem**: Lambda cold starts caused 3-5 second delays on first analysis, poor user experience.

**Solution**: 
- Optimized Lambda package size by removing unnecessary dependencies
- Increased memory to 1024MB for analyze Lambda (faster CPU allocation)
- Set timeout to 5 minutes for complex analysis
- Used Python 3.11 runtime for better performance
- Considered provisioned concurrency for production (stayed in Free Tier for now)

## What's Next

ContractGuard is live and functional, but there's more I want to build:

- **Multi-language support**: Analyze contracts in Hindi, Tamil, Telugu, and other Indian languages (currently English only)
- **Contract templates**: Pre-vetted templates for common scenarios (freelance agreements, NDAs, rental leases)
- **Comparison mode**: Upload two versions of a contract and see what changed with diff highlighting
- **Mobile app**: Native iOS and Android apps for on-the-go analysis
- **Legal expert review**: Option to escalate high-risk contracts to human lawyers for paid consultation
- **Contract negotiation assistant**: AI-powered chatbot to help draft counter-proposals
- **Bulk analysis**: Upload multiple contracts and get comparative risk analysis

## Try It Yourself

ContractGuard is live at: **https://d3cel0medhyrga.cloudfront.net/**

Upload any contract (rental agreement, employment contract, NDA, service agreement) and see the analysis in action. The app is free to use and requires no signup.

## About Me

I'm a software developer and AI engineer based in Pune, India, passionate about building technology that solves real problems for everyday people. I specialize in full-stack development, cloud architecture, and AI integration.

ContractGuard was born from watching friends and family sign contracts they didn't understand. I built this to change that.

**Connect with me:**
- LinkedIn: [Your LinkedIn URL]
- GitHub: [Your GitHub URL]
- Email: [Your Email]

---

## Resources

- **Live App**: https://d3cel0medhyrga.cloudfront.net/
- **GitHub Repository**: [Add your repo URL]
- **AWS Services Used**: 
  - Compute: Lambda (Python 3.11)
  - Storage: S3, DynamoDB
  - AI/ML: Bedrock (Nova Pro), Textract, Comprehend
  - Networking: CloudFront, API Gateway
  - Security: Cognito
  - Monitoring: CloudWatch
- **Tech Stack**: 
  - Frontend: React, TypeScript, Vite, TailwindCSS, shadcn/ui
  - Backend: Python, AWS CDK, boto3, PyPDF2, ReportLab
  - Infrastructure: AWS CDK (Python)

---

*Built with AWS Free Tier • Powered by Amazon Bedrock • Made in India 🇮🇳*
