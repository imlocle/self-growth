# Deployment Procedures & Infrastructure

**For: DevOps & Infrastructure Engineers**

**Last Updated:** March 12, 2026

---

## Table of Contents

1. [Deployment Architecture](#deployment-architecture)
2. [Prerequisites](#prerequisites)
3. [Local Development Deployment](#local-development-deployment)
4. [Staging Deployment](#staging-deployment)
5. [Production Deployment](#production-deployment)
6. [Infrastructure Management](#infrastructure-management)
7. [Rollback Procedures](#rollback-procedures)
8. [Monitoring & Alerts](#monitoring--alerts)

---

## Deployment Architecture

### Multi-Environment Setup

```
Development (Local)
  ↓ (git push)
Staging (AWS)
  ↓ (manual approval)
Production (AWS)
```

### AWS Infrastructure Stack

```
┌─────────────────────────────────────┐
│  CloudFront / Route 53              │ Optional: CDN and DNS
└──────────────┬───­────────────────────┘
               │
┌──────────────▼────────────────────────┐
│  API Gateway (HTTP API)               │
│  - JWT Authorizer (Cognito)           │
│  - Throttling & Rate Limiting         │
│  - CORS Configuration                 │
└──────────────┬───────────────────────┘
               │
      ┌────────┴────────┐
      │ Routes to       │
      │ Lambda Handler  │
      │ Based on Path   │
      │
  ┌───▼───────────────┐
  │ Lambda Functions  │ (37 total)
  │ - Python 3.13     │
  │ - Shared Layer    │
  │ - 256-512 MB RAM  │
  └───┬───────────────┘
      │
  ┌───▼──────────────────────┐
  │  DynamoDB Table          │
  │  "self_growth"           │
  │  - Single Table Design   │
  │  - PAY_PER_REQUEST Mode  │
  │  - Global Secondary Idx  │
  └───┬──────────────────────┘
      │
  ┌───▼──────────────────────┐
  │  Cognito User Pool       │
  │  - JWT Verification      │
  │  - User Management       │
  │  - MFA Support           │
  └──────────────────────────┘

Monitoring & Logging:
  - CloudWatch Logs (all Lambda stdout/stderr)
  - CloudWatch Metrics (duration, errors, throttles)
  - CloudWatch Alarms (high error rate, latency, etc.)
```

---

## Prerequisites

### Required AWS Permissions

Your IAM user needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:DeleteFunction",
        "lambda:InvokeFunction",
        "lambda:PublishVersion",
        "lambda:CreateAlias",
        "lambda:UpdateAlias"
      ],
      "Resource": "arn:aws:lambda:*:*:function/self-growth-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "apigateway:*",
        "dynamodb:*",
        "cognito-idp:*",
        "iam:*",
        "s3:*",
        "cloudwatch:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Required Tools

```bash
# Check installed versions
aws --version          # AWS CLI v2.x
terraform -version    # >= 1.0
python --version      # 3.13
make --version        # GNU Make
docker --version      # Docker Desktop or equivalent
```

### AWS Configuration

```bash
# Configure credentials
aws configure

# Verify access
aws sts get-caller-identity
# Output: UserId, Account, Arn
```

---

## Local Development Deployment

### 1. Local Setup (No AWS Needed)

```bash
# Install dependencies
make install-dev

# Run tests locally
make test

# Run linting
make lint

# All tests should pass (99 out of 111 expected)
```

### 2. Mock Deployment (Local Testing)

```bash
# Run Lambda locally with SAM (optional)
sam local start-api

# Alternative: Run with mocked AWS
python -m pytest tests/test_integration.py -v

# Verify mocked handlers work
pytest tests/ -k "test_create_habit" -v
```

---

## Staging Deployment

### 1. Prepare for Deployment

```bash
# Update version if needed
# Edit: src/__init__.py, terraform/variables.tf

# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ...commit and test locally...

# Ensure all tests pass
make test

# Lint code
make lint
```

### 2. Build Artifacts

```bash
# Build Lambda layer
make build

# Expected: lambda_layer/python/ directory populated

# Verify layer size
du -sh lambda_layer/python/

# Verify lambda packaged
make package

# Expected: lambda.zip created with ~5-50MB size
```

### 3. Deploy to Staging

```bash
# Set staging environment
export ENVIRONMENT=staging
export AWS_REGION=us-west-1

# Plan deployment (review resources)
cd terraform
terraform plan -var="environment=staging"

# Expected: Shows Lambda functions, DynamoDB table, API Gateway resources

# Apply deployment
terraform apply -var="environment=staging"

# Confirm when prompted (review resource changes)

# Deployment time: ~2-3 minutes
```

### 4. Verify Staging Deployment

```bash
# Get API endpoint
terraform output api_endpoint
# Output: https://abc123.execute-api.us-west-1.amazonaws.com/staging

# Test health check
curl https://abc123.execute-api.us-west-1.amazonaws.com/staging/health

# Test signup
curl -X POST https://abc123.execute-api.us-west-1.amazonaws.com/staging/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TempPassword123!"
  }'

# Expected: 201 Created with user details

# Check logs
aws logs tail /aws/lambda/auth-signup --follow

# Smoke test critical flows
pytest tests/test_integration.py -v --tb=short
```

### 5. Run Integration Tests Against Staging

```bash
# Configure tests to use staging
export API_ENDPOINT=https://abc123.execute-api.us-west-1.amazonaws.com/staging

# Run integration tests
pytest tests/test_integration.py -v

# Run end-to-end workflow tests
pytest tests/ -k "workflow" -v

# Expected: All tests pass (or document any staging-specific issues)
```

---

## Production Deployment

### ⚠️ Production Deployment Checklist

Before deploying to production, complete all items:

- [ ] All tests passing locally (99/111)
- [ ] Code reviewed and approved (1+ reviewers)
- [ ] Staging deployment verified
- [ ] Integration tests pass against staging
- [ ] Database backups created
- [ ] Rollback plan documented
- [ ] Monitoring dashboard reviewed
- [ ] Maintenance window scheduled (if needed)
- [ ] Deployment plan documented
- [ ] Team notified

### 1. Pre-Deployment Preparation

```bash
# Create backup of current state
aws dynamodb create-backup --table-name self_growth --backup-name pre-deploy-$(date +%s)

# Verify current production version
aws lambda list-functions | grep self-growth

# Make final checks
terraform plan -var="environment=production" > /tmp/plan.txt
cat /tmp/plan.txt | grep -c "No changes" || echo "⚠️ Changes detected, review carefully"
```

### 2. Production Deployment

```bash
# Set production environment
export ENVIRONMENT=production
export AWS_REGION=us-west-1

# Apply Terraform (PRODUCTION)
cd terraform
terraform apply -var="environment=production" -auto-approve=false

# Carefully review the output
# Expected resources to update/create:
# - Lambda functions (37 total)
# - API Gateway routes (37 total)
# - DynamoDB table (if not already exists)
# - Cognito resources (if not already exists)

# Confirm changes when prompted (type 'yes')
# Deployment time: 3-5 minutes
```

### 3. Post-Deployment Verification

```bash
# Health check
curl https://api.example.com/health

# Test authentication flow
curl -X POST https://api.example.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test+$(date +%s)@example.com",
    "password": "TempPassword123!"
  }'

# Verify API responses
curl https://api.example.com/habits -H "Authorization: Bearer <valid-token>"

# Check CloudWatch logs
aws logs tail /aws/lambda/habit-create --follow

# Monitor error rate
aws metrics-statistics --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=habit-create \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum

# Expected: Few to no errors in first 5 minutes
```

### 4. Smoke Tests Against Production

```bash
# Run subset of tests against production
# (Don't create heavy load testing)

pytest tests/test_integration.py::test_get_user_habits_workflow -v
pytest tests/test_integration.py::test_create_and_track_habit_workflow -v
pytest tests/test_controllers.py -v -k "test_get"

# Expected: All tests pass
```

### 5. Notify Users/Team

```bash
# Send deployment notification
echo "✅ Production deployment complete

Deployed Version: $(git rev-parse --short HEAD)
Timestamp: $(date)
API Endpoint: https://api.example.com
Status: All systems operational

Changes deployed: $(git log HEAD~5..HEAD --oneline)"
```

---

## Infrastructure Management

### Terraform State Management

```bash
# State stored in Terraform Cloud (remote)
# File: backend.auto.hcl

# View state
terraform show

# List all resources
terraform state list

# Inspect specific resource
terraform state show aws_lambda_function.habit_create

# Backup state (automatic, but manual backup too)
terraform state pull > /tmp/backup.tfstate
```

### Adding/Removing Lambda Functions

**Add a new handler:**

```hcl
# terraform/modules/lambda/main.tf

resource "aws_lambda_function" "new_handler" {
  filename      = data.archive_file.code.output_path
  function_name = "new-handler"
  role          = aws_iam_role.lambda_role.arn
  handler       = "src/handlers/new_domain/new_handler.lambda_handler"
  runtime       = "python3.13"
  # ... other config
  layers        = [aws_lambda_layer_version.dependencies.arn]
}

# Register with API Gateway
resource "aws_apigatewayv2_route" "new_handler" {
  api_id             = aws_apigatewayv2_api.api.id
  route_key          = "POST /new-endpoint"
  target             = "integrations/${aws_apigatewayv2_integration.new_handler.id}"
  authorization_type = "AWS_IAM"
}
```

**Remove a handler:**

```hcl
# Comment out or delete resource blocks
# Then: terraform apply

# Or manually delete:
aws lambda delete-function --function-name old-handler
```

### Modifying DynamoDB Schema

```hcl
# terraform/modules/dynamodb/main.tf

# Change attributes
resource "aws_dynamodb_table" "self_growth" {
  # ... existing config

  # Add new GSI
  global_secondary_index {
    name            = "GSI3"
    hash_key        = "GSI3PK"
    range_key       = "GSI3SK"
    projection_type = "ALL"
  }
}

# Apply changes
terraform apply

# Update queries in repositories accordingly
```

---

## Rollback Procedures

### Scenario 1: Deployment Broke Functionality

```bash
# Immediate action: Rollback to previous version
git revert HEAD
git push

# Redeploy with previous code
cd terraform
terraform apply -var="environment=production"

# Verify rollback
curl https://api.example.com/health

# Post-mortem: Debug issue and redeploy correctly
```

### Scenario 2: Database Corruption

```bash
# Restore from backup
aws dynamodb restore-table-from-backup \
  --backup-arn arn:aws:dynamodb:...:backup/... \
  --target-table-name self_growth_restored

# Verify data
aws dynamodb scan --table-name self_growth_restored

# Swap table names (update code/Terraform)
# Or restore directly if table name matches

# If problems occurred, restore from timestamped backup files
```

### Scenario 3: Lambda Layer Issue

```bash
# Rebuild layer
make build

# Force redeploy layer
cd terraform
terraform taint aws_lambda_layer_version.dependencies
terraform apply -var="environment=production"

# Lambda functions automatically use new layer
```

### Scenario 4: Scale Too High/Too Low

```bash
# For DynamoDB (PAY_PER_REQUEST mode)
# - Automatically scales, no action needed

# For Lambda concurrency limits
# Edit Terraform:
resource "aws_lambda_provisioned_concurrency_config" {
  function_name                     = aws_lambda_function.habit_create.function_name
  provisioned_concurrent_executions = 10  # Increase if needed
  qualifier                         = "LIVE"
}

terraform apply
```

---

## Monitoring & Alerts

### CloudWatch Dashboards

```bash
# Create custom dashboard
aws cloudwatch put-dashboard --dashboard-name \
  self-growth-production --dashboard-body '{
    "widgets": [
      {
        "type": "metric",
        "region": "us-west-1",
        "metrics": [
          ["AWS/Lambda", "Duration", {"stat": "Average"}],
          ["AWS/Lambda", "Errors", {"stat": "Sum"}],
          ["AWS/Lambda", "Throttles", {"stat": "Sum"}]
        ]
      }
    ]
  }'
```

### Key Metrics to Monitor

| Metric              | Threshold | Action                              |
| ------------------- | --------- | ----------------------------------- |
| Lambda Error Rate   | >1%       | Check logs, investigate             |
| Average Duration    | >2s       | Optimize code/layer                 |
| DynamoDB Throttling | Any       | Scale capacity/optimize queries     |
| API 4xx Errors      | >5%       | Check client requests               |
| API 5xx Errors      | >0.1%     | Check server logs                   |
| Cold Starts         | >10%      | Warm up functions or optimize layer |

### Setting Up Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name self-growth-high-errors \
  --alarm-description "Lambda error rate >1%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-west-1:...:team-alerts

# High latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name self-growth-high-latency \
  --metric-name Duration \
  --statistic Average \
  --threshold 2000 \
  --comparison-operator GreaterThanThreshold
```

### Viewing Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/habit-create --follow

# Logs from specific time
aws logs tail /aws/lambda/habit-create --since 1h

# Search for errors
aws logs tail /aws/lambda/habit-create \
  --filter-pattern "ERROR" \
  --since 30m

# Aggregate logs from all functions
aws logs tail /aws/lambda/ --follow --since 5m
```

---

## Troubleshooting Deployments

### Issue: "Resource already exists"

```bash
# Import existing resource into Terraform state
terraform import aws_dynamodb_table.self_growth self_growth

# Then: terraform apply (should show no changes)
```

### Issue: "Lambda execution role not found"

```bash
# Create IAM role if missing
aws iam create-role --role-name lambda-self-growth-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy --role-name lambda-self-growth-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### Issue: "Timeout waiting for DynamoDB table"

```bash
# Check if table exists
aws dynamodb describe-table --table-name self_growth

# If not, create it manually or check Terraform output
terraform output
```

### Issue: "Invalid IAM policy"

```bash
# Validate policy syntax
aws iam validate-custom-policy --policy-document file://policy.json

# Check policy permissions
aws iam get-user-policy --user-name myuser --policy-name mypoilcy
```

---

## Disaster Recovery

### Regular Backups

```bash
# Daily backup
aws dynamodb create-backup \
  --table-name self_growth \
  --backup-name daily-$(date +%Y%m%d)

# List backups
aws dynamodb list-backups --table-name self_growth

# Restore from backup (creates new table)
aws dynamodb restore-table-from-backup \
  --backup-arn arn:aws:dynamodb:...:backup/... \
  --target-table-name self_growth_restored
```

### Point-in-Time Recovery

```bash
# Enable PITR (if not already enabled)
aws dynamodb update-continuous-backups \
  --table-name self_growth \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Restore to specific point in time
aws dynamodb restore-table-to-point-in-time \
  --source-table-name self_growth \
  --target-table-name self_growth_recovered \
  --restore-date-time 2026-03-12T10:00:00Z
```

---

**Last Updated:** March 12, 2026
