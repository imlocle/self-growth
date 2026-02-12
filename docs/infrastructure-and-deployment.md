# Infrastructure and Deployment

## AWS Architecture Overview

The Self-Growth backend is built on a serverless architecture using AWS services with infrastructure managed through Terraform.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (HTTP API)                   │
│                  (JWT Authorizer: Cognito)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
   │ Auth    │      │ ToDo    │     │ Habit   │
   │ Lambdas │      │ Lambdas │     │ Lambdas │
   └────┬────┘      └────┬────┘     └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                    ┌────▼────────┐
                    │  DynamoDB   │
                    │ Single Table│
                    └─────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
   ┌────▼────┐                      ┌────▼────┐
   │ Cognito │                      │ Lambda  │
   │User Pool│                      │ Layer   │
   └─────────┘                      └─────────┘
```

## AWS Resources

### Cognito User Pool

**Resource Name:** `self-growth-user-pool-{env}`

**Configuration:**

- **Username Attribute:** email
- **Auto-verified Attributes:** email
- **Password Policy:**
  - Minimum length: 8 characters
  - Requires: uppercase, lowercase, numbers, symbols
- **Account Recovery:** verified email only
- **Custom Attributes:**
  - `phone_number` (string)
  - `given_name` (string)
  - `family_name` (string)

**Token Lifetimes:**

- Access Token: 1 day (86400 seconds)
- ID Token: 1 day (86400 seconds)
- Refresh Token: 3650 days (10 years)

**Authentication Flows:**

- `USER_PASSWORD_AUTH` (username/password)
- `REFRESH_TOKEN_AUTH` (refresh tokens)
- `USER_SRP_AUTH` (Secure Remote Password)

### Cognito User Pool Client

**Resource Name:** `self-growth-app-client-{env}`

**Configuration:**

- **OAuth Flows:** Authorization Code Flow
- **OAuth Scopes:** openid, email, profile
- **Prevent User Existence Errors:** Enabled (security best practice)
- **Supported Identity Providers:** Cognito User Pool
- **Callback URLs:** Configured per environment
- **Logout URLs:** Configured per environment

### DynamoDB Single Table

**Resource Name:** `self-growth-{env}`

**Table Configuration:**

- **Billing Mode:** Pay-per-request (on-demand)
- **Partition Key (PK):** String
- **Sort Key (SK):** String
- **Point-in-time Recovery:** Enabled
- **Encryption:** AWS managed keys

**Key Patterns:**

**Partition Key (PK):**

- `AUTHUSER#{user_id}` - User profile data
- `HOUSEHOLD#{household_id}` - All household-scoped data

**Sort Key (SK) Hierarchy:**

- `META#PROFILE` - User profile metadata
- `META#HOUSEHOLD` - Household metadata
- `MEMBER#{user_id}` - Household membership records
- `SUBJECT#{subject_id}` - Subject information
- `SUBJECT#{subject_id}#TODO#{todo_id}` - Todo items
- `SUBJECT#{subject_id}#HABIT#{habit_id}` - Habit definitions
- `SUBJECT#{subject_id}#HABIT#{habit_id}#EVENT#{period_key}` - Habit events

**Access Patterns:**

- Get user profile: PK=`AUTHUSER#{user_id}`, SK=`META#PROFILE`
- Get household data: PK=`HOUSEHOLD#{household_id}`, SK begins_with `META#`
- Get subject todos: PK=`HOUSEHOLD#{household_id}`, SK begins_with `SUBJECT#{subject_id}#TODO#`
- Get habit events: PK=`HOUSEHOLD#{household_id}`, SK begins_with `SUBJECT#{subject_id}#HABIT#{habit_id}#EVENT#`

### API Gateway (HTTP API)

**Resource Name:** `self-growth-api-{env}`

**Configuration:**

- **Protocol:** HTTP API (not REST API)
- **CORS:** Enabled for all origins (configurable per environment)
- **Throttling:** Default AWS limits
- **Logging:** CloudWatch logs enabled

**JWT Authorizer:**

- **Identity Source:** `$request.header.Authorization`
- **JWT Audience:** Cognito User Pool Client ID
- **JWT Issuer:** Cognito User Pool URL
- **Token Validation:** Automatic signature verification

**Route Mappings:**

```
POST   /auth/signup                                           → signup-lambda
POST   /auth/login                                            → login-lambda
POST   /auth/confirm-signup                                   → confirm-signup-lambda
POST   /user-profile                                          → create-user-profile-lambda
GET    /user-profile                                          → get-user-profile-lambda
POST   /households/{householdId}/subjects/{subjectId}/todos   → create-todo-lambda
GET    /households/{householdId}/subjects/{subjectId}/todos   → get-all-todo-lambda
GET    /households/{householdId}/subjects/{subjectId}/todos/{todoId} → get-todo-lambda
PUT    /households/{householdId}/subjects/{subjectId}/todos/{todoId} → update-todo-lambda
DELETE /households/{householdId}/subjects/{subjectId}/todos/{todoId} → delete-todo-lambda
POST   /households/{householdId}/subjects/{subjectId}/habits  → create-habit-lambda
GET    /households/{householdId}/subjects/{subjectId}/habits  → get-all-habit-lambda
GET    /households/{householdId}/subjects/{subjectId}/habits/{habitId} → get-habit-lambda
PUT    /households/{householdId}/subjects/{subjectId}/habits/{habitId} → update-habit-lambda
POST   /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events → create-habit-event-lambda
```

### Lambda Functions

**Runtime:** Python 3.13
**Architecture:** x86_64

**Common Configuration:**

- **Memory:** 256 MB (configurable per function)
- **Timeout:** 30 seconds
- **Environment Variables:**
  - `SELF_GROWTH_TABLE`: DynamoDB table name
  - `COGNITO_CLIENT_ID`: Cognito User Pool Client ID
- **IAM Role:** Lambda execution role with DynamoDB and Cognito permissions

**Function List:**

**Authentication Functions:**

- `self-growth-create-user-profile-{env}`
- `self-growth-get-user-profile-{env}`
- `self-growth-signup-{env}`
- `self-growth-login-{env}`
- `self-growth-confirm-signup-{env}`

**ToDo Functions:**

- `self-growth-create-todo-{env}`
- `self-growth-get-todo-{env}`
- `self-growth-get-all-todo-{env}`
- `self-growth-update-todo-{env}`
- `self-growth-delete-todo-{env}`

**Habit Functions:**

- `self-growth-create-habit-{env}`
- `self-growth-get-habit-{env}`
- `self-growth-get-all-habit-{env}`
- `self-growth-update-habit-{env}`

**Habit Event Functions:**

- `self-growth-create-habit-event-{env}`

### Lambda Layer

**Resource Name:** `self-growth-python-layer-{env}`

**Contents:**

- `boto3` - AWS SDK for Python
- `botocore` - Core AWS library
- `dataclasses-json` - JSON serialization for dataclasses
- `pytest` - Testing framework
- Additional Python dependencies from `src/requirements.txt`

**Benefits:**

- Shared dependencies across all Lambda functions
- Reduced deployment package size
- Faster cold starts
- Consistent dependency versions

## Terraform Infrastructure

### Module Structure

```
terraform/
├── main.tf                 # Main orchestration
├── variables.tf            # Input variables
├── outputs.tf              # Output values (API endpoint)
├── backend.auto.hcl        # S3 backend configuration
└── modules/
    ├── cognito/            # User Pool and Client
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── dynamodb/           # DynamoDB table
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── api/                # API Gateway and Authorizer
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── lambda/             # Lambda functions and layer
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

### Backend Configuration

**S3 State Backend:**

- **Bucket:** `self-growth-terraform-state-bucket`
- **Key Pattern:** `self-growth/{env}/terraform.tfstate`
- **Region:** us-west-1
- **Encryption:** AES256
- **Versioning:** Enabled
- **DynamoDB Lock Table:** `terraform-state-lock`

### Environment Variables

**Terraform Variables:**

```hcl
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "self-growth"
}
```

**Lambda Environment Variables:**

```hcl
environment {
  variables = {
    SELF_GROWTH_TABLE = module.dynamodb.table_name
    COGNITO_CLIENT_ID = module.cognito.client_id
    AWS_REGION       = var.region
  }
}
```

## Build and Deployment System

### Makefile Targets

**Primary Targets:**

```bash
make deploy ENV=dev              # Full deployment (build + terraform)
make deploy-create-todo ENV=dev  # Deploy single Lambda function
make rebuild-layer ENV=dev       # Force rebuild Lambda layer
make zip-all ENV=dev            # Build all Lambda zips
make nuke && make deploy ENV=dev # Full reset and redeploy
```

**Build Targets:**

```bash
make build-layer ENV=dev        # Build Lambda layer only
make zip-lambda FUNCTION=create-todo ENV=dev  # Build single Lambda zip
make terraform-init ENV=dev     # Initialize Terraform
make terraform-apply ENV=dev    # Apply Terraform changes
```

### Build Process

**1. Lambda Layer Build:**

```bash
# Check if requirements.txt changed
if [ src/requirements.txt -nt terraform/builds/python.zip ]; then
    # Create virtual environment
    python -m venv .layer_build
    source .layer_build/bin/activate

    # Install dependencies
    pip install -r src/requirements.txt -t lambda_layer/python/

    # Create zip
    cd lambda_layer && zip -r ../terraform/builds/python.zip python/
fi
```

**2. Lambda Function Build:**

```bash
# For each function (e.g., create-todo)
mkdir -p build/create-todo
cp -r src/ build/create-todo/
cd build/create-todo
zip -r ../../terraform/builds/self-growth-create-todo-${ENV}.zip .
```

**3. Terraform Deployment:**

```bash
cd terraform
terraform init -backend-config="key=self-growth/${ENV}/terraform.tfstate"
terraform apply -var="environment=${ENV}" -auto-approve
```

### Incremental Build Optimization

**Layer Rebuild Conditions:**

- `src/requirements.txt` modified
- `lambda_layer/python/.built` missing
- Force rebuild flag set

**Lambda Rebuild Conditions:**

- Source files in `src/` modified
- Lambda zip missing
- Layer rebuilt (dependency change)

**Terraform Apply Conditions:**

- Infrastructure files modified
- Lambda zips updated
- Environment variables changed

## Deployment Workflow

### Development Deployment

**1. Local Setup:**

```bash
# Clone repository
git clone <repository-url>
cd self-growth-backend

# Set up Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt

# Configure AWS credentials
aws configure
```

**2. Deploy to Development:**

```bash
# Full deployment
make deploy ENV=dev

# Check deployment
curl https://api-dev.self-growth.com/health
```

**3. Single Function Update:**

```bash
# Update specific function
make deploy-create-todo ENV=dev

# Verify function
aws lambda invoke --function-name self-growth-create-todo-dev response.json
```

### Production Deployment

**1. Environment Preparation:**

```bash
# Ensure production AWS profile
export AWS_PROFILE=production

# Validate Terraform plan
cd terraform
terraform plan -var="environment=prod"
```

**2. Production Deploy:**

```bash
# Deploy with confirmation
make deploy ENV=prod

# Verify deployment
make test-endpoints ENV=prod
```

**3. Rollback Process:**

```bash
# Rollback to previous version
git checkout <previous-commit>
make deploy ENV=prod

# Or rollback specific function
aws lambda update-function-code \
  --function-name self-growth-create-todo-prod \
  --zip-file fileb://previous-version.zip
```

### Environment Management

**Development Environment:**

- **Purpose:** Feature development and testing
- **Data:** Test data, can be reset
- **Access:** Development team
- **Monitoring:** Basic CloudWatch logs

**Staging Environment (Future):**

- **Purpose:** Pre-production testing
- **Data:** Production-like test data
- **Access:** QA team and stakeholders
- **Monitoring:** Full monitoring stack

**Production Environment:**

- **Purpose:** Live user traffic
- **Data:** Real user data
- **Access:** Operations team only
- **Monitoring:** Full observability, alerting

## Monitoring and Observability

### Current Monitoring

**CloudWatch Logs:**

- Lambda function execution logs
- API Gateway access logs
- Error logs with stack traces

**CloudWatch Metrics:**

- Lambda invocations, errors, duration
- API Gateway request count, latency, errors
- DynamoDB consumed capacity, throttling

**DynamoDB Metrics:**

- Read/write capacity consumption
- Throttled requests
- System errors

### Recommended Enhancements

**1. X-Ray Tracing:**

```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch AWS SDK calls
patch_all()

@xray_recorder.capture('todo_service.create')
def create(self, user_id, household_id, subject_id, data):
    # Service implementation
    pass
```

**2. Custom Metrics:**

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def put_custom_metric(metric_name: str, value: float, unit: str = 'Count'):
    cloudwatch.put_metric_data(
        Namespace='SelfGrowth',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Dimensions': [
                    {
                        'Name': 'Environment',
                        'Value': os.environ.get('ENVIRONMENT', 'dev')
                    }
                ]
            }
        ]
    )

# Usage in services
put_custom_metric('TodoCreated', 1)
put_custom_metric('HabitEventLogged', 1)
```

**3. CloudWatch Alarms:**

```hcl
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "self-growth-lambda-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors lambda errors"

  dimensions = {
    FunctionName = "self-growth-create-todo-${var.environment}"
  }
}
```

## Security Considerations

### IAM Roles and Policies

**Lambda Execution Role:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:BatchGetItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/self-growth-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminCreateUser",
        "cognito-idp:AdminSetUserPassword",
        "cognito-idp:AdminGetUser"
      ],
      "Resource": "arn:aws:cognito-idp:*:*:userpool/*"
    }
  ]
}
```

### Network Security

**VPC Configuration (Optional):**

- Lambda functions can run in VPC for enhanced security
- Private subnets for Lambda functions
- NAT Gateway for internet access
- Security groups for network-level access control

**API Gateway Security:**

- JWT token validation
- Rate limiting per client
- Request/response validation
- CORS configuration

### Data Security

**Encryption:**

- DynamoDB encryption at rest (AWS managed keys)
- API Gateway TLS 1.2+ for data in transit
- Lambda environment variables encryption

**Access Control:**

- Cognito User Pool for authentication
- JWT tokens for API authorization
- Path parameter validation in services
- Household membership validation

## Cost Optimization

### Current Cost Structure

**DynamoDB:**

- Pay-per-request billing
- No provisioned capacity
- Scales automatically with usage

**Lambda:**

- Pay per invocation and duration
- 256MB memory allocation
- Shared layer reduces package size

**API Gateway:**

- HTTP API (cheaper than REST API)
- Pay per request
- No caching configured

### Cost Optimization Strategies

**1. Lambda Optimization:**

- Right-size memory allocation based on profiling
- Optimize cold start times
- Use provisioned concurrency for high-traffic functions

**2. DynamoDB Optimization:**

- Monitor read/write patterns
- Consider reserved capacity for predictable workloads
- Implement data archiving for old records

**3. API Gateway Optimization:**

- Enable caching for read-heavy endpoints
- Implement request/response compression
- Use regional endpoints instead of edge-optimized

## Disaster Recovery

### Backup Strategy

**DynamoDB:**

- Point-in-time recovery enabled
- Automated backups retained for 35 days
- Cross-region backup replication (future)

**Code and Infrastructure:**

- Git repository with version control
- Terraform state in S3 with versioning
- Lambda deployment packages archived

### Recovery Procedures

**1. Data Recovery:**

```bash
# Restore DynamoDB table to specific point in time
aws dynamodb restore-table-to-point-in-time \
  --source-table-name self-growth-prod \
  --target-table-name self-growth-prod-restored \
  --restore-date-time 2025-01-01T12:00:00Z
```

**2. Infrastructure Recovery:**

```bash
# Restore from Terraform state
cd terraform
terraform import aws_dynamodb_table.main self-growth-prod
terraform apply -var="environment=prod"
```

**3. Application Recovery:**

```bash
# Redeploy from known good commit
git checkout <stable-commit>
make deploy ENV=prod
```

### Business Continuity

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 1 hour

**Procedures:**

1. Incident detection and notification
2. Assessment and decision to recover
3. Infrastructure restoration
4. Data recovery and validation
5. Application deployment and testing
6. Service restoration and monitoring
