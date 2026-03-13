# Requirements Document

## Introduction

This feature adds an intermediate `upload_completed` status to the contract upload workflow to explicitly track when a file successfully lands in S3 before analysis begins. Currently, the workflow transitions directly from `pending_upload` to `analyzing`, which doesn't provide visibility into whether the S3 upload succeeded. The new status will improve observability and debugging capabilities by clearly separating the upload completion event from the analysis start event.

## Glossary

- **Analyze_Lambda**: The AWS Lambda function triggered by S3 events that processes uploaded contract PDFs
- **Contract**: A PDF document uploaded by a user for analysis
- **Contract_Status**: An enumerated field tracking the lifecycle state of a contract (pending_upload, upload_completed, analyzing, completed, failed)
- **S3_Event**: An event notification triggered when an object is created in the S3 bucket
- **Status_Transition**: A change from one contract status to another, logged for debugging purposes

## Requirements

### Requirement 1: Upload Completion Status

**User Story:** As a system operator, I want to track when a contract file successfully lands in S3, so that I can distinguish between upload failures and analysis failures.

#### Acceptance Criteria

1. WHEN the Analyze_Lambda is triggered by an S3 event, THE Analyze_Lambda SHALL update the Contract_Status to "upload_completed"
2. WHEN the Contract_Status is updated to "upload_completed", THE Analyze_Lambda SHALL log the status transition with the contract ID and timestamp
3. WHEN the Contract_Status update to "upload_completed" fails, THE Analyze_Lambda SHALL log the error and continue processing

### Requirement 2: Analysis Status Transition

**User Story:** As a system operator, I want the analyzing status to be set when text extraction begins, so that I can track when analysis actually starts.

#### Acceptance Criteria

1. WHEN text extraction begins for a contract, THE Analyze_Lambda SHALL update the Contract_Status from "upload_completed" to "analyzing"
2. WHEN the Contract_Status is updated to "analyzing", THE Analyze_Lambda SHALL log the status transition with the contract ID and timestamp
3. THE Analyze_Lambda SHALL maintain the existing text extraction logic without modification

### Requirement 3: Error Handling Preservation

**User Story:** As a system operator, I want existing error handling to remain functional, so that failed uploads and analyses are still tracked correctly.

#### Acceptance Criteria

1. WHEN an error occurs during contract processing, THE Analyze_Lambda SHALL update the Contract_Status to "failed"
2. WHEN the Contract_Status is updated to "failed", THE Analyze_Lambda SHALL log the error details including contract ID and error message
3. THE Analyze_Lambda SHALL preserve all existing error handling logic and exception propagation

### Requirement 4: Status Flow Validation

**User Story:** As a developer, I want to ensure the status flow follows the correct sequence, so that the system maintains data integrity.

#### Acceptance Criteria

1. THE Analyze_Lambda SHALL transition Contract_Status in the sequence: pending_upload → upload_completed → analyzing → (completed OR failed)
2. WHEN processing a contract, THE Analyze_Lambda SHALL not skip the "upload_completed" status
3. THE Analyze_Lambda SHALL log all status transitions for debugging and audit purposes
