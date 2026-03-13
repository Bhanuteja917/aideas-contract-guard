# Implementation Plan: Contract Upload Status Tracking

## Overview

This implementation adds an intermediate `upload_completed` status to the contract upload workflow by modifying the analyze Lambda function. The change is minimal and focused: adding a single status update call immediately after retrieving the contract record from DynamoDB, before the existing `analyzing` status update.

## Tasks

- [x] 1. Add upload_completed status update to analyze Lambda
  - Modify `lambda_handler` function in `backend/lambda/analyze/lambda_function.py`
  - Add `update_contract_status(contract_id, 'upload_completed')` call after `get_contract_by_id()` succeeds
  - Add log statement: `print(f"Updated contract {contract_id} status to upload_completed")`
  - Place the new code before the existing `update_contract_status(contract_id, 'analyzing')` call
  - Ensure the new status update is within the existing try/except block
  - _Requirements: 1.1, 1.2_

- [ ]* 1.1 Write property test for upload_completed status update
  - **Property 1: Upload Completion Status Update**
  - **Validates: Requirements 1.1**
  - Generate random S3 events with valid contract IDs
  - Mock DynamoDB and verify `update_contract_status` called with "upload_completed"
  - Verify status update occurs before text extraction
  - _Requirements: 1.1_

- [ ]* 1.2 Write property test for status transition logging
  - **Property 4: Status Transition Logging**
  - **Validates: Requirements 1.2, 2.2, 4.3**
  - Generate random status transitions
  - Capture log output and verify each transition logged with contract ID and timestamp
  - Test for all status values: upload_completed, analyzing, completed, failed
  - _Requirements: 1.2, 2.2, 4.3_

- [ ] 2. Verify analyzing status update placement
  - Review existing `update_contract_status(contract_id, 'analyzing')` call
  - Ensure it remains immediately before `extract_text_from_pdf()` call
  - Verify log statement exists: `print(f"Updated contract {contract_id} status to analyzing")`
  - Confirm no changes needed to existing code
  - _Requirements: 2.1, 2.2_

- [ ]* 2.1 Write property test for analyzing status update timing
  - **Property 2: Analyzing Status Update Before Extraction**
  - **Validates: Requirements 2.1**
  - Generate random contracts
  - Mock text extraction function
  - Verify `update_contract_status` called with "analyzing" before text extraction
  - _Requirements: 2.1_

- [ ] 3. Checkpoint - Verify status updates and logging
  - Run the Lambda function with test S3 events
  - Verify both status updates occur in correct order
  - Verify log output contains both transitions with contract IDs
  - Ensure all tests pass, ask the user if questions arise

- [ ]* 3.1 Write property test for status transition sequence
  - **Property 3: Status Transition Sequence**
  - **Validates: Requirements 4.1, 4.2**
  - Generate random successful processing flows
  - Track all status updates during execution
  - Verify sequence: pending_upload → upload_completed → analyzing → (completed OR failed)
  - Verify no status is skipped
  - _Requirements: 4.1, 4.2_

- [ ]* 3.2 Write property test for error handling status
  - **Property 5: Error Handling Status Update**
  - **Validates: Requirements 3.1**
  - Generate random error conditions (DynamoDB failures, text extraction failures)
  - Verify status updated to "failed" for all error types
  - Verify error is propagated after status update
  - _Requirements: 3.1_

- [ ]* 3.3 Write property test for error logging
  - **Property 6: Error Logging Completeness**
  - **Validates: Requirements 3.2**
  - Generate random errors during processing
  - Capture log output when status set to "failed"
  - Verify logs contain both contract ID and error message
  - _Requirements: 3.2_

- [ ]* 3.4 Write unit tests for edge cases
  - Test invalid S3 key format handling
  - Test contract not found scenario
  - Test DynamoDB update failure for upload_completed status
  - Test that processing continues after non-critical errors
  - _Requirements: 1.3, 3.1, 3.2_

- [ ] 4. Final checkpoint - Verify complete implementation
  - Run all tests (unit and property tests)
  - Verify status flow works end-to-end
  - Verify error handling preserves existing behavior
  - Review logs to ensure all transitions are captured
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The core implementation (Task 1) is minimal: adding one status update call and one log statement
- Existing error handling and text extraction logic remain completely unchanged
- Property tests use `pytest` with `hypothesis` library, minimum 100 iterations each
- Each property test references its design document property for traceability
