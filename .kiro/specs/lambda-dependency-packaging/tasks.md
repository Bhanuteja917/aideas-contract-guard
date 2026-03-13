# Implementation Plan: Lambda Dependency Packaging

## Overview

This implementation plan converts the ContractGuard Lambda functions from basic `lambda_.Function` constructs to `PythonFunction` constructs that automatically package Python dependencies. The approach is incremental: update infrastructure dependencies, migrate each Lambda function one at a time, and verify functionality after each change.

## Tasks

- [x] 1. Update CDK infrastructure dependencies
  - Add `aws-cdk.aws-lambda-python-alpha` to `backend/infrastructure/requirements.txt`
  - Install updated dependencies in the infrastructure virtual environment
  - _Requirements: 2.1, 2.3_

- [x] 2. Migrate Upload Lambda to PythonFunction
  - [x] 2.1 Update Upload Lambda construct in contract_guard_stack.py
    - Import `PythonFunction` from `aws_cdk.aws_lambda_python_alpha`
    - Replace `lambda_.Function` with `PythonFunction` for Upload Lambda
    - Update handler specification to use `index` and `handler` parameters
    - Keep all existing configuration (environment variables, permissions, timeout, memory)
    - _Requirements: 1.1, 2.2, 2.3_
  
  - [ ]* 2.2 Write property test for Upload Lambda dependency packaging
    - **Property 1: Complete Dependency Packaging**
    - **Validates: Requirements 1.1, 2.2, 2.3**
  
  - [ ]* 2.3 Write unit test for Upload Lambda runtime imports
    - Deploy Upload Lambda and invoke with test payload
    - Verify boto3 imports successfully
    - _Requirements: 1.2_

- [x] 3. Migrate Analyze Lambda to PythonFunction
  - [x] 3.1 Update Analyze Lambda construct in contract_guard_stack.py
    - Replace `lambda_.Function` with `PythonFunction` for Analyze Lambda
    - Update handler specification to use `index` and `handler` parameters
    - Keep all existing configuration (environment variables, permissions, timeout, memory)
    - _Requirements: 1.1, 2.2, 2.3_
  
  - [ ]* 3.2 Write property test for Analyze Lambda dependency packaging
    - **Property 1: Complete Dependency Packaging**
    - **Validates: Requirements 1.1, 2.2, 2.3**
  
  - [ ]* 3.3 Write unit test for Analyze Lambda PyPDF2 import
    - Deploy Analyze Lambda and invoke with test payload
    - Verify PyPDF2 and boto3 import successfully
    - _Requirements: 1.2_

- [x] 4. Migrate Report Lambda to PythonFunction
  - [x] 4.1 Update Report Lambda construct in contract_guard_stack.py
    - Replace `lambda_.Function` with `PythonFunction` for Report Lambda
    - Update handler specification to use `index` and `handler` parameters
    - Keep all existing configuration (environment variables, permissions, timeout, memory)
    - _Requirements: 1.1, 2.2, 2.3_
  
  - [ ]* 4.2 Write property test for Report Lambda dependency packaging
    - **Property 1: Complete Dependency Packaging**
    - **Validates: Requirements 1.1, 2.2, 2.3**
  
  - [ ]* 4.3 Write unit test for Report Lambda runtime imports
    - Deploy Report Lambda and invoke with test payload
    - Verify boto3 imports successfully
    - _Requirements: 1.2_

- [x] 5. Checkpoint - Verify all Lambda functions deploy successfully
  - Run `cdk synth` to verify CDK stack synthesizes without errors
  - Run `cdk deploy` to deploy all three Lambda functions
  - Verify deployment logs show dependency installation for each Lambda
  - Ensure all tests pass, ask the user if questions arise

- [ ]* 6. Write property test for dependency isolation
  - [ ]* 6.1 Create test Lambda functions with conflicting dependency versions
    - **Property 5: Dependency Isolation**
    - **Validates: Requirements 3.1, 3.3**

- [ ]* 7. Write property test for platform compatibility
  - [ ]* 7.1 Verify binary dependencies are Linux x86_64 compatible
    - **Property 3: Platform-Compatible Dependencies**
    - **Validates: Requirements 1.4**

- [ ]* 8. Write property test for automatic dependency installation
  - [ ]* 8.1 Verify cdk deploy triggers automatic dependency installation
    - **Property 4: Automatic Dependency Installation**
    - **Validates: Requirements 2.1**

- [ ]* 9. Write property test for build logging
  - [ ]* 9.1 Verify CDK output logs installed packages
    - **Property 6: Build Logging Transparency**
    - **Validates: Requirements 4.2**

- [ ]* 10. Write unit test for missing dependency error handling
  - Create test Lambda with non-existent package in requirements.txt
  - Verify `cdk deploy` fails with clear error message
  - Verify error message includes package name and diagnostic information
  - _Requirements: 1.3, 2.4, 4.3_

- [ ]* 11. Write unit test for Docker availability error handling
  - Mock Docker unavailability scenario
  - Verify deployment fails with actionable error message
  - _Requirements: 2.4_

- [ ]* 12. Write integration test for end-to-end Lambda functionality
  - Deploy all three Lambda functions
  - Test Upload Lambda with file upload
  - Test Analyze Lambda with PDF processing (verify PyPDF2 works)
  - Test Report Lambda with report generation
  - Verify all functions work correctly with packaged dependencies
  - _Requirements: 1.2, 1.4_

- [ ] 13. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify all Lambda functions are operational in deployed environment
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each Lambda migration is independent and can be tested individually
- The PythonFunction construct requires Docker to be installed and running
- Build times will increase slightly due to dependency packaging, but this is a one-time cost per deployment
- CDK will cache built dependencies, so subsequent deployments of unchanged Lambdas are fast
- All existing Lambda configuration (environment variables, IAM permissions, timeouts) remains unchanged
