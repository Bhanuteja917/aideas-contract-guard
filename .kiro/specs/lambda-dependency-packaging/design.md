# Design Document: Lambda Dependency Packaging

## Overview

This design addresses the Lambda dependency packaging problem in the ContractGuard project. Currently, Lambda functions use the basic `aws_lambda.Function` construct which deploys only the source code without dependencies, causing runtime import errors. The solution migrates to the `aws_lambda_python_alpha.PythonFunction` construct, which automatically packages Python dependencies using Docker to ensure compatibility with the Lambda runtime environment.

The design focuses on minimal changes to the existing CDK infrastructure while ensuring all three Lambda functions (upload, analyze, report) have their dependencies properly packaged and isolated.

## Architecture

### Current Architecture Issues

The current CDK stack uses `lambda_.Function` with `lambda_.Code.from_asset()` pointing to Lambda directories:

```python
lambda_.Function(
    self,
    "AnalyzeLambda",
    runtime=lambda_.Runtime.PYTHON_3_11,
    handler="lambda_function.lambda_handler",
    code=lambda_.Code.from_asset("../lambda/analyze"),
    # ... other config
)
```

This approach only packages the Python source files, ignoring `requirements.txt`. Dependencies like PyPDF2 are not included in the deployment package.

### Proposed Architecture

Replace `lambda_.Function` with `PythonFunction` from the `aws_lambda_python_alpha` module:

```python
from aws_cdk.aws_lambda_python_alpha import PythonFunction

PythonFunction(
    self,
    "AnalyzeLambda",
    entry="../lambda/analyze",
    runtime=lambda_.Runtime.PYTHON_3_11,
    index="lambda_function.py",
    handler="lambda_handler",
    # ... other config
)
```

The `PythonFunction` construct:
- Automatically detects `requirements.txt` in the entry directory
- Uses Docker to install dependencies in a Lambda-compatible environment
- Bundles dependencies with source code into a deployment package
- Maintains dependency isolation per function

### Build Process Flow

```
CDK Synth/Deploy
    ↓
PythonFunction construct detects requirements.txt
    ↓
Docker container spins up (Amazon Linux 2 - Lambda runtime)
    ↓
pip install -r requirements.txt --target ./package
    ↓
Bundle source code + dependencies
    ↓
Create deployment package (ZIP)
    ↓
Upload to S3 (CDK asset bucket)
    ↓
Lambda function references S3 asset
```

## Components and Interfaces

### Modified Components

#### 1. ContractGuardStack (contract_guard_stack.py)

**Changes:**
- Import `PythonFunction` from `aws_cdk.aws_lambda_python_alpha`
- Replace three `lambda_.Function` constructs with `PythonFunction`
- Update handler specification (split into `index` and `handler` parameters)
- Keep all other configuration (environment variables, permissions, timeouts) unchanged

**Interface:**
- Input: Lambda source directories with requirements.txt
- Output: Deployed Lambda functions with bundled dependencies

#### 2. Infrastructure Requirements (requirements.txt)

**Changes:**
- Add `aws-cdk.aws-lambda-python-alpha` dependency

**New dependency:**
```
aws-cdk.aws-lambda-python-alpha==2.125.0a0
```

### Component Interactions

```
CDK Stack Definition
    ↓
PythonFunction Construct
    ↓ (reads)
Lambda Source Directory
    ├── lambda_function.py
    └── requirements.txt
    ↓ (builds)
Docker Build Environment
    ↓ (produces)
Lambda Deployment Package
    ├── lambda_function.py
    └── site-packages/
        ├── PyPDF2/
        ├── boto3/
        └── ...
```

## Data Models

### Lambda Directory Structure

Each Lambda function directory maintains the same structure:

```
lambda/{function_name}/
├── lambda_function.py      # Handler code
└── requirements.txt        # Python dependencies
```

### PythonFunction Configuration

```python
PythonFunction(
    self,
    construct_id: str,           # Unique construct identifier
    entry: str,                  # Path to Lambda directory
    runtime: Runtime,            # Python runtime version
    index: str,                  # Handler file name (without .py)
    handler: str,                # Handler function name
    function_name: str,          # Lambda function name
    environment: dict,           # Environment variables
    timeout: Duration,           # Execution timeout
    memory_size: int,            # Memory allocation
)
```

### Deployment Package Structure

The resulting deployment package contains:

```
deployment-package.zip
├── lambda_function.py           # Source code
└── [dependency packages]        # Installed from requirements.txt
    ├── PyPDF2/
    ├── boto3/
    ├── botocore/
    └── ...
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Complete Dependency Packaging

*For any* Lambda function with a requirements.txt file, the deployed Lambda package should contain all packages listed in requirements.txt along with their transitive dependencies.

**Validates: Requirements 1.1, 2.2, 2.3**

### Property 2: Runtime Import Success

*For any* Lambda function with packaged dependencies, invoking the function should successfully import all modules listed in requirements.txt without ImportError exceptions.

**Validates: Requirements 1.2**

### Property 3: Platform-Compatible Dependencies

*For any* Lambda function with binary dependencies, the packaged dependencies should be compiled for the Linux x86_64 architecture compatible with the Lambda runtime environment.

**Validates: Requirements 1.4**

### Property 4: Automatic Dependency Installation

*For any* Lambda function with a requirements.txt file, running `cdk deploy` should automatically trigger dependency installation without requiring manual build steps.

**Validates: Requirements 2.1**

### Property 5: Dependency Isolation

*For any* two Lambda functions with different versions of the same dependency, each deployed Lambda package should contain its own specified version without interference.

**Validates: Requirements 3.1, 3.3**

### Property 6: Build Logging Transparency

*For any* Lambda function deployment, the CDK build output should log which packages and versions were installed during the dependency packaging process.

**Validates: Requirements 4.2**

### Example Tests

#### Example 1: Missing Dependency Error Handling

When a requirements.txt file specifies a non-existent package (e.g., `nonexistent-package==1.0.0`), the `cdk deploy` command should fail with a clear error message indicating which package could not be found.

**Validates: Requirements 1.3, 2.4, 4.3**

## Error Handling

### Dependency Installation Failures

**Scenario:** A package in requirements.txt cannot be installed (doesn't exist, version not found, network error)

**Handling:**
- PythonFunction construct fails during CDK synthesis/deployment
- Error message includes:
  - Package name and version that failed
  - pip error output
  - Suggestion to check package name and version
- Deployment is halted before any resources are created/updated

### Docker Availability Issues

**Scenario:** Docker is not installed or not running on the deployment machine

**Handling:**
- PythonFunction construct detects missing Docker
- Error message clearly states: "Docker is required for PythonFunction construct"
- Provides instructions to install/start Docker
- Deployment fails early with actionable error

### Platform Compatibility Issues

**Scenario:** A dependency requires compilation but fails on Lambda's platform

**Handling:**
- Docker build process captures compilation errors
- Error message includes build logs showing compilation failure
- Suggests checking if package supports Linux x86_64
- Deployment fails with diagnostic information

### Requirements File Issues

**Scenario:** requirements.txt is malformed or contains invalid syntax

**Handling:**
- pip fails to parse requirements.txt
- Error message shows line number and syntax issue
- Deployment fails with pip's error output
- Suggests fixing requirements.txt syntax

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit tests**: Verify specific deployment scenarios, error conditions, and edge cases
- **Property tests**: Verify universal properties across different Lambda configurations and dependency combinations

### Property-Based Testing

**Library:** Use `hypothesis` for Python-based property testing

**Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with: `Feature: lambda-dependency-packaging, Property {N}: {property_text}`

**Test Implementation:**

Each correctness property should be implemented as a property-based test:

1. **Property 1 Test**: Generate Lambda functions with various requirements.txt files, deploy them, and verify all packages are in the deployment package
2. **Property 2 Test**: Generate Lambda functions with different dependencies, deploy and invoke them, verify no ImportError occurs
3. **Property 3 Test**: Generate Lambda functions with binary dependencies, verify packages are Linux x86_64 compatible
4. **Property 4 Test**: Generate Lambda configurations, run cdk deploy, verify dependencies are installed automatically
5. **Property 5 Test**: Generate pairs of Lambda functions with conflicting dependency versions, verify each has correct isolated version
6. **Property 6 Test**: Generate Lambda deployments, capture CDK output, verify package installation is logged

### Unit Testing

**Focus Areas:**
- Specific example: Deploy analyze Lambda with PyPDF2, verify it can import and use PyPDF2
- Edge case: Empty requirements.txt file (should deploy successfully with no dependencies)
- Edge case: requirements.txt with only comments (should deploy successfully)
- Error condition: Invalid package name in requirements.txt (should fail with clear error)
- Error condition: Docker not available (should fail with actionable error message)
- Integration: Verify all three Lambda functions (upload, analyze, report) deploy successfully with their respective dependencies

### Testing Constraints

**Limitations:**
- Property 3.2 (selective rebuild optimization) is not tested as it's a build performance characteristic, not a correctness requirement
- Requirement 4.1 (package inspection tooling) is not tested as it's a developer experience feature, not a functional requirement

### Test Environment

**Requirements:**
- Docker installed and running
- AWS credentials configured
- CDK CLI installed
- Test AWS account with Lambda deployment permissions
- Ability to create/destroy Lambda functions for testing

**Test Isolation:**
- Each test should use unique Lambda function names
- Tests should clean up created resources after completion
- Use CDK test constructs or separate test stacks
