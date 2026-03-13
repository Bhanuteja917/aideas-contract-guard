# Implementation Plan: ContractGuard

## Overview

This implementation plan breaks down the ContractGuard project into discrete coding tasks that build incrementally toward a complete AI-powered contract analysis tool. The plan follows a 4-week timeline aligned with the AWS 10,000 AIdeas Competition deadline (March 13, 2026). Each task builds on previous work, with checkpoints to ensure quality and allow for user feedback.

## Tasks

### Phase 1: Infrastructure and Project Setup (Week 1)

- [x] 1. Initialize project structure and dependencies
  - Create monorepo structure with frontend and backend directories
  - Initialize TypeScript configuration for both frontend and backend
  - Set up package.json with required dependencies (React, AWS SDK v3, AWS CDK, fast-check, Jest)
  - Configure ESLint and Prettier for code quality
  - Create .gitignore for Node.js and AWS artifacts
  - _Requirements: 12.1, 13.2_

- [x] 2. Implement AWS CDK infrastructure stack
  - [x] 2.1 Create CDK app and ContractGuardStack class
    - Define stack with environment parameter (dev/prod)
    - Set up CDK app entry point
    - _Requirements: 12.1, 13.1_
  
  - [x] 2.2 Define S3 buckets for frontend, contracts, and reports
    - Configure encryption, lifecycle rules, and access policies
    - Set up frontend bucket for static website hosting
    - _Requirements: 11.1, 11.2, 12.1_
  
  - [x] 2.3 Create CloudFront distribution for frontend delivery
    - Configure origin, caching, and HTTPS redirect
    - Set up SPA routing with error responses
    - _Requirements: 12.2, 12.4_
  
  - [x] 2.4 Set up Cognito User Pool for authentication
    - Configure email-based sign-up and sign-in
    - Set password policy and email verification
    - Create user pool client for web app
    - _Requirements: 10.1, 10.2_
  
  - [x] 2.5 Create DynamoDB tables for contracts and analyses
    - Define partition keys and GSIs
    - Configure encryption and billing mode
    - _Requirements: 11.1_
  
  - [x] 2.6 Define Lambda function placeholders and IAM roles
    - Create Lambda function constructs with environment variables
    - Grant S3, DynamoDB, and AI service permissions
    - Set up S3 event trigger for analyze Lambda
    - _Requirements: 13.2, 13.3_
  
  - [x] 2.7 Create API Gateway with Cognito authorizer
    - Define REST API with CORS configuration
    - Create endpoints: POST /contracts, GET /contracts/{id}, GET /contracts/{id}/report
    - Attach Cognito authorizer to endpoints
    - _Requirements: 13.1, 13.3_
  
  - [x] 2.8 Add CloudWatch log groups and alarms
    - Create log groups for each Lambda function
    - Set up alarms for Free Tier limit warnings
    - _Requirements: 14.1, 14.2_
  
  - [x] 2.9 Deploy infrastructure to AWS
    - Run cdk bootstrap for first-time setup
    - Execute cdk deploy and capture outputs
    - Verify all resources created successfully
    - _Requirements: 12.1, 13.1_

- [x] 3. Checkpoint - Infrastructure verification
  - Verify all AWS resources are created and accessible
  - Test API Gateway endpoints return 401 (no auth yet)
  - Confirm S3 buckets are accessible with proper permissions
  - Ask user if questions arise

### Phase 2: Frontend Foundation (Week 1-2)

- [x] 4. Set up React frontend application
  - [x] 4.1 Initialize React app with Vite and TypeScript
    - Configure Vite for development and production builds
    - Set up TypeScript configuration for React
    - Install and configure Tailwind CSS
    - _Requirements: 12.1_
  
  - [x] 4.2 Create authentication context and hooks
    - Implement AuthContext with Cognito integration
    - Create useAuth hook for sign-up, sign-in, sign-out
    - Handle JWT token storage and refresh
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ]* 4.3 Write property tests for authentication logic
    - **Property 17: Authentication rejection consistency**
    - **Validates: Requirements 10.3**
  
  - [x] 4.4 Create authentication UI components
    - Build SignUp component with email and password fields
    - Build SignIn component with error handling
    - Build ProtectedRoute wrapper for authenticated pages
    - _Requirements: 10.1, 10.2, 10.3_

- [x] 5. Implement file upload component
  - [x] 5.1 Create UploadComponent with drag-and-drop
    - Implement file drop zone with visual feedback
    - Add file picker button as alternative
    - Display selected file information
    - _Requirements: 1.1, 1.2_
  
  - [x] 5.2 Implement file validation logic
    - Check file size (max 10MB)
    - Check file type (PDF only)
    - Display validation errors to user
    - _Requirements: 1.3, 1.4_
  
  - [ ]* 5.3 Write property tests for file validation
    - **Property 1: File size validation consistency**
    - **Property 2: File type validation consistency**
    - **Validates: Requirements 1.3, 1.4**
  
  - [x] 5.4 Implement upload progress tracking
    - Create progress state with percentage
    - Display progress bar during upload
    - Handle upload completion and errors
    - _Requirements: 1.5, 1.6_
  
  - [ ]* 5.5 Write property tests for upload progress
    - **Property 3: Upload progress monotonicity**
    - **Validates: Requirements 1.5**
  
  - [x] 5.6 Integrate with upload API endpoint
    - Call POST /contracts/upload to get pre-signed URL
    - Upload file directly to S3 using pre-signed URL
    - Handle network errors with retry logic
    - _Requirements: 1.6, 15.1, 15.3_

- [x] 6. Checkpoint - Upload functionality
  - Test file upload end-to-end with real AWS services
  - Verify files appear in S3 contracts bucket
  - Verify contract records created in DynamoDB
  - Ask user if questions arise

### Phase 3: Backend Lambda Functions (Week 2)

- [x] 7. Implement Upload Lambda function
  - [x] 7.1 Create upload handler with input validation
    - Parse and validate request body (userId, fileName, fileSize, contentType)
    - Validate user authentication from Cognito JWT
    - Return 400 for invalid inputs
    - _Requirements: 1.3, 1.4, 10.4_
  
  - [ ]* 7.2 Write property tests for upload validation
    - **Property 1: File size validation consistency**
    - **Property 2: File type validation consistency**
    - **Validates: Requirements 1.3, 1.4**
  
  - [x] 7.3 Generate pre-signed S3 upload URL
    - Create unique contractId (UUID)
    - Generate S3 key with user prefix: `{userId}/{contractId}.pdf`
    - Create pre-signed URL with 15-minute expiration
    - _Requirements: 11.4, 11.5_
  
  - [ ]* 7.4 Write property tests for pre-signed URLs
    - **Property 21: File organization by user**
    - **Property 22: Pre-signed URL expiration**
    - **Validates: Requirements 11.4, 11.5**
  
  - [x] 7.5 Store contract metadata in DynamoDB
    - Create contract record with status "pending_upload"
    - Include userId, fileName, fileSize, s3Key, uploadedAt
    - Return contractId and uploadUrl to client
    - _Requirements: 11.1, 10.4_
  
  - [ ]* 7.6 Write property tests for contract ownership
    - **Property 18: Contract ownership association**
    - **Validates: Requirements 10.4**

- [x] 8. Implement Analyze Lambda function - Text extraction
  - [x] 8.1 Create analyze handler triggered by S3 events
    - Parse S3 event to get bucket and key
    - Update contract status to "analyzing" in DynamoDB
    - Set up error handling with CloudWatch logging
    - _Requirements: 2.1, 15.2_
  
  - [x] 8.2 Integrate Amazon Textract for text extraction
    - Call Textract DetectDocumentText API
    - Extract full text and block structure
    - Preserve paragraphs and sections
    - _Requirements: 2.1, 2.2_
  
  - [x] 8.3 Implement retry logic for Textract failures
    - Retry up to 3 times with exponential backoff
    - Log each retry attempt
    - Update contract status to "failed" after max retries
    - _Requirements: 2.3, 15.2_
  
  - [ ]* 8.4 Write property tests for retry logic
    - **Property 5: Text extraction retry limit**
    - **Validates: Requirements 2.3**

- [ ] 9. Implement Analyze Lambda function - Entity identification
  - [x] 9.1 Integrate Amazon Comprehend for entity detection
    - Call Comprehend DetectEntities API with extracted text
    - Identify PERSON, DATE, QUANTITY, ORGANIZATION entities
    - Store entities with text, type, score, and offsets
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 9.2 Write property tests for entity positions
    - **Property 6: Entity position validity**
    - **Validates: Requirements 3.4**

- [ ] 10. Implement Analyze Lambda function - Clause analysis
  - [x] 10.1 Integrate Amazon Bedrock with Claude model
    - Set up Bedrock client with Claude model ID
    - Create prompt template for contract analysis
    - Include Indian Contract Act context in prompt
    - _Requirements: 4.1, 7.1_
  
  - [x] 10.2 Implement clause analysis logic
    - Send extracted text and entities to Bedrock
    - Parse response to identify clauses and risk patterns
    - Detect: unfair liability, hidden fees, termination, IP, non-compete
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [x] 10.3 Implement risk scoring algorithm
    - Assign risk scores (1-10) to each identified risk
    - Calculate category scores: financial, legal liability, IP, termination
    - Calculate overall risk score as weighted average
    - _Requirements: 4.7, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 10.4 Write property tests for risk scoring
    - **Property 7: Risk score bounds**
    - **Property 8: Overall risk score calculation**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [ ] 11. Implement Analyze Lambda function - Explanations and compliance
  - [x] 11.1 Generate plain-language explanations
    - Create prompts for English and Hindi explanations
    - Call Bedrock for each clause with legal terminology
    - Highlight concerning provisions in explanations
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ]* 11.2 Write property tests for explanations
    - **Property 9: Explanation generation completeness**
    - **Property 10: Concerning provisions highlighted**
    - **Validates: Requirements 6.1, 6.2, 6.3**
  
  - [x] 11.3 Implement Indian Contract Act compliance checking
    - Create prompt with Indian Contract Act sections
    - Identify non-compliant clauses
    - Flag jurisdiction issues for non-Indian jurisdictions
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [ ]* 11.4 Write property tests for compliance
    - **Property 11: Jurisdiction detection**
    - **Property 12: Compliance findings inclusion**
    - **Validates: Requirements 7.3, 7.4**
  
  - [x] 11.5 Generate negotiation recommendations
    - Create recommendations for high-risk clauses (score ≥ 7)
    - Tailor recommendations for small businesses
    - _Requirements: 8.4_
  
  - [ ]* 11.6 Write property tests for recommendations
    - **Property 13: High-risk recommendation generation**
    - **Validates: Requirements 8.4**
  
  - [x] 11.7 Store complete analysis in DynamoDB
    - Create analysis record with all results
    - Link to contract via contractId
    - Update contract status to "completed"
    - _Requirements: 11.1_
  
  - [ ]* 11.8 Write property tests for data storage
    - **Property 20: S3 retrieval round-trip**
    - **Validates: Requirements 11.3**

- [x] 12. Checkpoint - Analysis pipeline
  - Upload test contract and verify analysis completes
  - Check DynamoDB for analysis results
  - Verify all risk scores are within bounds
  - Confirm explanations generated in both languages
  - Ask user if questions arise

### Phase 4: Dashboard and Visualization (Week 3)

- [ ] 13. Implement dashboard data fetching
  - [x] 13.1 Create API client for fetching analyses
    - Implement GET /contracts/{id} endpoint handler
    - Fetch contract and analysis from DynamoDB
    - Enforce user ownership check
    - _Requirements: 10.5_
  
  - [ ]* 13.2 Write property tests for data isolation
    - **Property 19: Data isolation**
    - **Validates: Requirements 10.5**
  
  - [x] 13.3 Create React hook for analysis data
    - Implement useAnalysis hook with loading states
    - Handle polling for in-progress analyses
    - Cache results to avoid redundant API calls
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 14. Build risk dashboard UI components
  - [x] 14.1 Create RiskScoreDisplay component
    - Display overall risk score prominently
    - Use color coding: green (1-3), yellow (4-6), red (7-10)
    - Show score as large number with visual indicator
    - _Requirements: 8.1, 8.5_
  
  - [ ]* 14.2 Write property tests for color coding
    - **Property 14: Risk color coding consistency**
    - **Validates: Requirements 8.5**
  
  - [x] 14.3 Create RiskCategoryChart component
    - Use Recharts to display bar chart of category scores
    - Show financial, legal liability, IP, termination categories
    - Apply color coding to each bar
    - _Requirements: 8.2, 8.5_
  
  - [x] 14.4 Create ClauseList component
    - Display clause-by-clause analysis
    - Show clause text, risk score, and concerns
    - Display English and Hindi explanations
    - Highlight high-risk clauses
    - _Requirements: 8.3, 6.1, 6.2, 6.3_
  
  - [x] 14.5 Create ComplianceSection component
    - Display compliance issues with severity indicators
    - Show Indian Contract Act section references
    - Highlight jurisdiction issues
    - _Requirements: 7.2, 7.3, 7.4_
  
  - [x] 14.6 Create RecommendationsSection component
    - Display negotiation recommendations
    - Group by risk category
    - Provide actionable advice for small businesses
    - _Requirements: 8.4_

- [x] 15. Checkpoint - Dashboard functionality
  - Test dashboard with multiple sample contracts
  - Verify all visualizations render correctly
  - Check color coding accuracy
  - Confirm bilingual explanations display properly
  - Ask user if questions arise

### Phase 5: Report Generation (Week 3)

- [ ] 16. Implement Report Lambda function
  - [x] 16.1 Create report handler with authorization
    - Parse contractId from path parameters
    - Validate user owns the contract
    - Fetch analysis from DynamoDB
    - _Requirements: 9.1, 10.5_
  
  - [x] 16.2 Implement PDF generation logic
    - Use PDFKit or similar library to create PDF
    - Include overall risk score section
    - Add risk category breakdown with charts
    - Include clause-by-clause analysis
    - Add compliance findings section
    - Include negotiation recommendations
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6_
  
  - [ ]* 16.3 Write property tests for report completeness
    - **Property 15: Report content completeness**
    - **Validates: Requirements 9.2, 9.3, 9.4, 9.5, 9.6**
  
  - [x] 16.4 Store PDF in S3 and return download URL
    - Save generated PDF to reports bucket
    - Generate pre-signed download URL (15 min expiration)
    - Return URL to client
    - _Requirements: 9.7, 11.5_
  
  - [ ]* 16.5 Write property tests for download URLs
    - **Property 16: Report download URL validity**
    - **Validates: Requirements 9.7**

- [ ] 17. Add report download to frontend
  - [x] 17.1 Create ReportDownload component
    - Add "Download Report" button to dashboard
    - Call GET /contracts/{id}/report endpoint
    - Handle loading state during generation
    - Trigger browser download with PDF
    - _Requirements: 9.1, 9.7_
  
  - [x] 17.2 Implement error handling for report generation
    - Display user-friendly errors if generation fails
    - Provide retry option
    - Log errors for debugging
    - _Requirements: 15.1, 15.3, 15.4_

- [x] 18. Checkpoint - Report generation
  - Generate reports for test contracts
  - Verify PDF contains all required sections
  - Check PDF formatting and readability
  - Test download functionality in browser
  - Ask user if questions arise

### Phase 6: Error Handling and Polish (Week 4)

- [ ] 19. Implement comprehensive error handling
  - [ ] 19.1 Add error boundaries to React components
    - Wrap app in ErrorBoundary component
    - Display user-friendly error messages
    - Provide recovery options (retry, go home)
    - _Requirements: 15.1, 15.4_
  
  - [ ]* 19.2 Write property tests for error messages
    - **Property 25: User-friendly error messages**
    - **Property 28: Error explanation completeness**
    - **Validates: Requirements 15.1, 15.4, 15.5**
  
  - [ ] 19.3 Implement Lambda error handling
    - Wrap all Lambda operations in try-catch
    - Log errors with context to CloudWatch
    - Return structured error responses
    - _Requirements: 15.2_
  
  - [ ]* 19.4 Write property tests for error logging
    - **Property 26: Error logging completeness**
    - **Validates: Requirements 15.2**
  
  - [ ] 19.5 Add retry mechanisms for AWS service failures
    - Implement exponential backoff for Textract, Comprehend, Bedrock
    - Allow users to retry failed analyses
    - Display retry options in UI
    - _Requirements: 15.3_
  
  - [ ]* 19.6 Write property tests for retry availability
    - **Property 27: Retry availability after failure**
    - **Validates: Requirements 15.3**

- [ ] 20. Implement AWS Free Tier monitoring
  - [ ] 20.1 Create usage tracking Lambda function
    - Query CloudWatch metrics for service usage
    - Calculate percentage of Free Tier limits
    - Store usage data in DynamoDB
    - _Requirements: 14.1_
  
  - [ ] 20.2 Implement warning system
    - Check usage against 80% threshold
    - Log warnings to CloudWatch
    - Send notifications (optional: SNS/email)
    - _Requirements: 14.2_
  
  - [ ]* 20.3 Write property tests for warning thresholds
    - **Property 24: Free Tier warning threshold**
    - **Validates: Requirements 14.2**

- [ ] 21. Add loading states and user feedback
  - [ ] 21.1 Implement loading indicators
    - Add spinners for API calls
    - Show progress for file uploads
    - Display "Analyzing..." state during processing
    - _Requirements: 1.5_
  
  - [ ] 21.2 Add success notifications
    - Show toast messages for successful uploads
    - Confirm when analysis completes
    - Notify when report is ready
    - _Requirements: 1.6, 9.7_
  
  - [ ] 21.3 Improve error messages
    - Make all error messages user-friendly
    - Avoid technical jargon
    - Suggest corrective actions
    - _Requirements: 15.1, 15.4, 15.5_

- [ ] 22. Checkpoint - Error handling and monitoring
  - Test error scenarios (invalid files, network failures, AWS errors)
  - Verify error messages are user-friendly
  - Check CloudWatch logs for proper error logging
  - Confirm retry mechanisms work correctly
  - Ask user if questions arise

### Phase 7: Testing and Documentation (Week 4)

- [ ] 23. Run comprehensive test suite
  - [ ] 23.1 Execute all property-based tests
    - Run fast-check tests with 100+ iterations
    - Verify all 28 correctness properties pass
    - Fix any failing tests
    - _Requirements: All_
  
  - [ ] 23.2 Execute unit tests
    - Run Jest tests for all components and functions
    - Achieve >80% code coverage
    - Fix any failing tests
    - _Requirements: All_
  
  - [ ] 23.3 Perform integration testing
    - Test complete upload-to-report workflow
    - Test with various contract types and sizes
    - Verify bilingual explanations
    - Test error scenarios
    - _Requirements: All_

- [ ] 24. Create sample contracts for demo
  - [ ] 24.1 Prepare 3-5 sample contracts
    - Low-risk contract (score 1-3)
    - Medium-risk contract (score 4-6)
    - High-risk contract (score 7-10)
    - Contract with compliance issues
    - Contract with jurisdiction issues
    - _Requirements: All_
  
  - [ ] 24.2 Test all samples through system
    - Upload each contract
    - Verify analysis results
    - Generate reports
    - Take screenshots for article
    - _Requirements: All_

- [ ] 25. Write competition article
  - [ ] 25.1 Draft article content
    - Problem statement and target audience
    - Solution architecture with diagrams
    - Social impact for Indian small businesses
    - Technical implementation details
    - AWS services used and Free Tier compliance
    - Demo screenshots and results
    - Future enhancements
    - _Requirements: All_
  
  - [ ] 25.2 Create demo video
    - Record 2-3 minute walkthrough
    - Show upload, analysis, dashboard, report download
    - Highlight key features and social impact
    - _Requirements: All_
  
  - [ ] 25.3 Finalize and publish article
    - Review and edit article
    - Add all screenshots and video
    - Publish by March 13, 2026, 4:00 AM IST
    - _Requirements: All_

- [ ] 26. Final checkpoint - Competition submission
  - Verify article is published
  - Test deployed application end-to-end
  - Confirm all AWS services within Free Tier
  - Ensure demo video is accessible
  - Celebrate completion!

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and allow for user feedback
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- Timeline is aggressive (29 days) - prioritize core functionality over polish if needed
- AWS Free Tier limits must be monitored throughout development
