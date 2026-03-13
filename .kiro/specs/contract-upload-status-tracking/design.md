# Design Document: Contract Upload Status Tracking

## Overview

This design adds an intermediate `upload_completed` status to the contract upload workflow by modifying the analyze Lambda function. The change introduces a two-stage status update pattern: first marking the upload as complete when the S3 event triggers the Lambda, then transitioning to analyzing when text extraction begins. This provides clear visibility into the upload success event separate from the analysis start event.

The implementation is minimal and focused, requiring changes only to the `lambda_handler` function in `backend/lambda/analyze/lambda_function.py`. The existing `update_contract_status` function will be reused without modification.

## Architecture

The contract upload workflow involves three main components:

1. **Upload Lambda**: Creates pre-signed S3 URLs and sets initial status to `pending_upload`
2. **S3 Bucket**: Stores uploaded contract PDFs and triggers events on object creation
3. **Analyze Lambda**: Processes S3 events, extracts text, and performs analysis

This design modifies only the Analyze Lambda to add the intermediate status update.

### Current Flow

```
User uploads → Upload Lambda → pending_upload → S3 upload → S3 event → Analyze Lambda → analyzing → completed/failed
```

### New Flow

```
User uploads → Upload Lambda → pending_upload → S3 upload → S3 event → Analyze Lambda → upload_completed → analyzing → completed/failed
```

### Status Transition Points

1. **upload_completed**: Set immediately when Analyze Lambda is triggered by S3 event (confirms S3 upload succeeded)
2. **analyzing**: Set when text extraction begins (existing behavior, just moved later in the flow)
3. **completed/failed**: Set based on analysis outcome (unchanged)

## Components and Interfaces

### Modified Component: Analyze Lambda

**File**: `backend/lambda/analyze/lambda_function.py`

**Function**: `lambda_handler(event, context)`

The function will be modified to add a status update immediately after retrieving the contract record and before starting text extraction.

**Modification Points**:

1. After `get_contract_by_id()` succeeds, add:
   - Update status to `upload_completed`
   - Log the transition

2. Before `extract_text_from_pdf()` call, update:
   - Update status to `analyzing` (existing code, no change)
   - Log the transition (existing code, no change)

**Pseudocode**:

```python
def lambda_handler(event, context):
    for record in event['Records']:
        # Extract bucket, key, contract_id (unchanged)
        
        # Get contract record (unchanged)
        contract = get_contract_by_id(contract_id)
        
        # NEW: Update status to upload_completed
        update_contract_status(contract_id, 'upload_completed')
        log(f"Updated contract {contract_id} status to upload_completed")
        
        # EXISTING: Update status to analyzing
        update_contract_status(contract_id, 'analyzing')
        log(f"Updated contract {contract_id} status to analyzing")
        
        # Extract text and continue processing (unchanged)
```

### Unchanged Components

**Function**: `update_contract_status(contract_id, status)`
- No changes required
- Already supports arbitrary status values
- Handles DynamoDB updates and error logging

**Function**: `get_contract_by_id(contract_id)`
- No changes required

**Function**: `extract_text_from_pdf(bucket, key)`
- No changes required

**Error Handling**:
- Existing try/except blocks remain unchanged
- Failed status updates are already logged and handled

## Data Models

### Contract Status Field

**Field**: `status` (string)

**Valid Values**:
- `pending_upload`: Initial state after pre-signed URL creation
- `upload_completed`: NEW - File successfully uploaded to S3
- `analyzing`: Text extraction and analysis in progress
- `completed`: Analysis finished successfully
- `failed`: Upload or analysis failed

**Constraints**:
- Status transitions must follow the sequence: pending_upload → upload_completed → analyzing → (completed | failed)
- The `upload_completed` status is set by the Analyze Lambda when triggered by S3 event
- The `analyzing` status is set by the Analyze Lambda when text extraction begins

### DynamoDB Schema

**Table**: CONTRACTS_TABLE

**Relevant Fields**:
- `contractId` (string, partition key): Unique identifier
- `status` (string): Current contract status
- `updatedAt` (string, ISO 8601 timestamp): Last update time

**No schema changes required** - the status field already accepts string values.

## Correctness Properties


A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Upload Completion Status Update

*For any* valid S3 event triggering the Analyze Lambda with a valid contract ID, the contract status should be updated to "upload_completed" before any text extraction begins.

**Validates: Requirements 1.1**

### Property 2: Analyzing Status Update Before Extraction

*For any* contract being processed, the status should be updated to "analyzing" immediately before the text extraction function is called.

**Validates: Requirements 2.1**

### Property 3: Status Transition Sequence

*For any* contract processed successfully, the status transitions should follow the exact sequence: pending_upload → upload_completed → analyzing → (completed OR failed), with no status being skipped.

**Validates: Requirements 4.1, 4.2**

### Property 4: Status Transition Logging

*For any* status transition (to upload_completed, analyzing, completed, or failed), a log entry should be created containing the contract ID and a timestamp.

**Validates: Requirements 1.2, 2.2, 4.3**

### Property 5: Error Handling Status Update

*For any* error occurring during contract processing, the contract status should be updated to "failed" and the error should be propagated.

**Validates: Requirements 3.1**

### Property 6: Error Logging Completeness

*For any* error that causes a status update to "failed", the log output should contain both the contract ID and the error message.

**Validates: Requirements 3.2**

## Error Handling

The existing error handling strategy is preserved with no modifications:

1. **DynamoDB Errors**: If `update_contract_status()` fails, the error is logged and raised, causing the Lambda to fail and potentially retry
2. **Contract Not Found**: If `get_contract_by_id()` returns None, processing continues to the next record
3. **Text Extraction Errors**: If `extract_text_from_pdf()` fails, the exception is caught, status is set to "failed", and the error is raised
4. **General Processing Errors**: The outer try/except block catches all exceptions, attempts to set status to "failed", and raises the error

The new `upload_completed` status update is placed within the existing try/except block, so any failures will be handled by the existing error handling logic.

### Error Scenarios

1. **Status update to upload_completed fails**: Error is logged and raised, Lambda fails, S3 event may retry
2. **Status update to analyzing fails**: Error is logged and raised, Lambda fails, contract remains in upload_completed state
3. **Text extraction fails**: Existing error handling sets status to "failed" and logs the error

## Testing Strategy

### Unit Testing

Unit tests should focus on specific scenarios and edge cases:

1. **Status Update Verification**: Test that `update_contract_status` is called with correct parameters
2. **Logging Verification**: Test that log messages contain required information (contract ID, timestamp)
3. **Error Handling**: Test that errors during status updates are handled correctly
4. **Edge Cases**:
   - Invalid S3 key format
   - Contract not found in DynamoDB
   - DynamoDB update failures
   - Text extraction failures

### Property-Based Testing

Property tests should verify universal behaviors across many generated inputs:

1. **Property 1**: Generate random S3 events and contract IDs, verify upload_completed status is set
2. **Property 2**: Generate random contracts, verify analyzing status is set before text extraction
3. **Property 3**: Generate random processing flows, verify status sequence is correct
4. **Property 4**: Generate random status transitions, verify all are logged with contract ID and timestamp
5. **Property 5**: Generate random error conditions, verify failed status is set
6. **Property 6**: Generate random errors, verify logs contain contract ID and error message

**Configuration**:
- Use `pytest` with `hypothesis` library for property-based testing
- Each property test should run minimum 100 iterations
- Tag each test with: **Feature: contract-upload-status-tracking, Property {number}: {property_text}**

**Test Balance**:
- Unit tests handle specific examples and integration points
- Property tests handle comprehensive input coverage through randomization
- Both are necessary for complete validation

### Integration Testing

Integration tests should verify the complete flow:

1. Trigger Lambda with real S3 event
2. Verify status transitions in DynamoDB
3. Verify log output contains all expected entries
4. Verify error handling with simulated failures
