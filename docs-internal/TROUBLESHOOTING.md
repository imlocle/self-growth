# Troubleshooting Guide

**For: Debugging & Problem-Solving**

**Last Updated:** March 12, 2026

---

## Table of Contents

1. [Common Issues & Solutions](#common-issues--solutions)
2. [Lambda Function Issues](#lambda-function-issues)
3. [Database Issues](#database-issues)
4. [Authentication Issues](#authentication-issues)
5. [API Issues](#api-issues)
6. [Deployment Issues](#deployment-issues)
7. [Performance Issues](#performance-issues)
8. [Getting Help](#getting-help)

---

## Common Issues & Solutions

### "ModuleNotFoundError: No module named 'boto3'"

**Symptoms:**

- Lambda function fails immediately
- Error in CloudWatch logs

**Cause:** Lambda layer not included or out of date

**Solution:**

```bash
# Rebuild layer
make build

# Redeploy layer
cd terraform
terraform taint aws_lambda_layer_version.dependencies
terraform apply

# Verify layer deployed
aws lambda list-layers --query 'Layers[?LayerArn like `*self-growth*`]'
```

---

### "UnauthorizedError: JWT validation failed"

**Symptoms:**

- 401 Unauthorized responses
- "Token is invalid" error

**Cause:** JWT token expired or invalid

**Solution:**

```bash
# Check token expiry
jwt decode <token>  # See exp claim

# Get new token
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "..."}'

# Use refresh token
curl -X POST https://api.example.com/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

---

### "ValidationError: Title must be 1-200 characters"

**Symptoms:**

- 400 Bad Request with validation error
- Field is actually valid

**Cause:** Input sanitization removed valid content

**Solution:**

```python
# Check sanitization logic
from src.utils.validation import sanitize_html

test_input = "My Habit <script>alert('xss')</script>"
sanitized = sanitize_html(test_input)
print(f"Input: {test_input}")
print(f"Output: {sanitized}")

# If over-sanitizing, adjust validation.py
```

---

### "ConflictError: Email already registered"

**Symptoms:**

- 409 Conflict when signing up
- Same email can't be used twice

**Cause:** User already exists with that email

**Solution:**

```bash
# Option 1: Use different email
curl -X POST /auth/signup -d '{"email": "new@example.com", ...}'

# Option 2: Check if user exists
aws cognito-idp admin-get-user \
  --user-pool-id <pool-id> \
  --username <email>

# Option 3: Reset password instead
curl -X POST /auth/forgot-password -d '{"email": "existing@example.com"}'
```

---

## Lambda Function Issues

### Lambda Timeout (30 second limit)

**Problem:** Function execution exceeds 30 seconds

**Symptoms:**

```
Task timed out after 30.00 seconds
```

**Solutions:**

1. **Increase timeout:**

   ```bash
   aws lambda update-function-configuration \
     --function-name habit-create \
     --timeout 60
   ```

2. **Optimize function:**

   ```python
   # Profile to find bottleneck
   import time

   start = time.time()
   items = repo.query_by_user(user_id)  # Measure this
   print(f"Query took {time.time() - start}s")

   # If >5s, optimize query or add indexes
   ```

3. **Break into async tasks:**

   ```python
   # Instead of big operation, queue async job
   import sqs

   # Send message to queue
   sqs.send_message(QueueUrl=queue, MessageBody=json.dumps({
       "action": "calculate_analytics",
       "habit_id": habit_id
   }))

   # Separate Lambda processes queue
   # Main handler returns immediately
   ```

---

### "Container credential provider found, but attempted to retrieve credentials"

**Problem:** Lambda can't access AWS services

**Cause:** IAM role permissions missing or expired

**Solution:**

```bash
# Check Lambda execution role
aws lambda get-function-configuration --function-name habit-create \
  | jq '.Role'

# Check role permissions
aws iam list-role-policies --role-name lambda-self-growth-role

# Add missing permission
aws iam put-role-policy --role-name lambda-self-growth-role \
  --policy-name dynamodb-access \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": "dynamodb:*",
      "Resource": "arn:aws:dynamodb:*:*:table/self_growth"
    }]
  }'
```

---

### Cold Start Too Slow

**Problem:** First invocation after deployment takes 5-15 seconds

**Symptoms:**

```
Duration: 12345ms (for simple operation)
Cloud start latency unacceptable
```

**Solution:**

1. **Reduce Lambda package size:**

   ```bash
   # Check layer size
   du -sh lambda_layer/python/

   # Remove unnecessary packages
   # Rebuild: make build
   ```

2. **Increase memory (faster CPU):**

   ```bash
   aws lambda update-function-configuration \
     --function-name habit-create \
     --memory-size 512  # More memory = more CPU
   ```

3. **Use Provisioned Concurrency:**
   ```bash
   # Keep warm copies always running
   aws lambda put-provisioned-concurrency-config \
     --function-name habit-create \
     --provisioned-concurrent-executions 5
   ```

---

## Database Issues

### "ValidationException: One or more indices were not updated"

**Problem:** DynamoDB index creation failed

**Cause:** Schema conflict or index already exists

**Solution:**

```bash
# Check current table schema
aws dynamodb describe-table --table-name self_growth \
  | jq '.Table.GlobalSecondaryIndexes'

# Delete problematic index
aws dynamodb delete-table --table-name self_growth

# Recreate with terraform
terraform apply
```

---

### "ProvisionedThroughputExceededException"

**Problem:** DynamoDB requests being throttled

**Symptoms:**

```
ProvisionedThroughputExceededException:
The level of configured provisioned throughput for the table was exceeded
```

**Solution:**

1. **Switch to PAY_PER_REQUEST (recommended):**

   ```hcl
   # terraform/modules/dynamodb/main.tf
   billing_mode       = "PAY_PER_REQUEST"  # Instead of PROVISIONED
   # Cost scales with usage, not pre-provisioned
   ```

2. **Increase provisioned capacity (alternative):**

   ```bash
   aws dynamodb update-table \
     --table-name self_growth \
     --billing-mode PROVISIONED \
     --provisioned-throughput ReadCapacityUnits=100,WriteCapacityUnits=100
   ```

3. **Optimize queries:**

   ```python
   # Bad: Full table scan
   items = dynamodb.scan(TableName="self_growth")

   # Good: Query with partition key
   items = dynamodb.query(
       TableName="self_growth",
       KeyConditionExpression="PK = :pk",
       ExpressionAttributeValues={":pk": {"S": f"USER#{user_id}"}}
   )
   ```

---

### "Item size has exceeded the maximum allowed size"

**Problem:** Storing item >400KB

**Cause:** Habit with too much data

**Solution:**

```python
# Check item size before saving
import sys

item = habit.to_dynamo()
size_kb = sys.getsizeof(item) / 1024

if size_kb > 350:  # Leave margin
    print(f"Item too large: {size_kb}KB")
    # Archive old events or compress data

# Alternatively: Split large fields into separate items
habit_events = split_into_separate_table(habit.events)
```

---

## Authentication Issues

### "InvalidPasswordException"

**Problem:** Password doesn't meet Cognito requirements

**Symptoms:**

```
InvalidPasswordException: 1 validation error detected:
Value at 'password' failed to satisfy constraint:
Member must have length greater than or equal to 8
```

**Cognito Password Policy:**

- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 1 number (0-9)
- At least 1 special character (!@#$%^&\*)

**Solution:**

```
Valid: "SecurePass123!" ✅
Invalid: "password" ❌ (no uppercase, number, special)
Invalid: "Pass" ❌ (too short)
Invalid: "ALLUPPERCASE123!" ❌ (no lowercase)
```

---

### "UsernameExistsException"

**Problem:** Can't sign up with existing email

**Solution:**

```bash
# Check if user exists
aws cognito-idp admin-get-user \
  --user-pool-id <pool-id> \
  --username <email>

# Get user status
# Output: UserStatus: FORCE_CHANGE_PASSWORD | CONFIRMED | UNCONFIRMED

# If UNCONFIRMED, user never verified email
# Send new confirmation code
aws cognito-idp admin-initiate-auth \
  --user-pool-id <pool-id> \
  --client-id <client-id> \
  --auth-flow ADMIN_NO_SRP_AUTH \
  --auth-parameters USERNAME=<email>,PASSWORD=<password>

# Or delete and retry signup
aws cognito-idp admin-delete-user \
  --user-pool-id <pool-id> \
  --username <email> \
  --permanent  # Actually delete, not just disable
```

---

### "UserNotFoundException"

**Problem:** Can't login, user doesn't exist

**Solution:**

```bash
# Check user pool
aws cognito-idp list-users --user-pool-id <pool-id> \
  --filter "email = '<email>'"

# If no results, user never signed up
# Signup first: POST /auth/signup
```

---

## API Issues

### "CORS error: Access-Control-Allow-Origin not present"

**Problem:** Frontend can't call API from different domain

**Symptoms:**

```
Access to XMLHttpRequest at 'https://api.example.com/...'
from origin 'https://app.example.com' has been blocked by CORS policy
```

**Solution:**

1. **Check API Gateway CORS:**

   ```bash
   aws apigatewayv2 get-stages \
     --api-id <api-id> \
     | jq '.Stages[].DefaultRouteSettings.CorsPolicy'
   ```

2. **Update CORS configuration:**

   ```hcl
   # terraform/modules/api/main.tf
   default_route_settings = {
     cors_configuration {
       allow_credentials = true
       allow_headers     = ["*"]
       allow_methods     = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
       allow_origins     = [
         "https://app.example.com",
         "https://app-staging.example.com"
       ]
       expose_headers    = ["x-amzn-RequestId"]
       max_age          = 300
     }
   }

   # terraform apply
   ```

---

### "404 Not Found"

**Problem:** Endpoint doesn't exist

**Solution:**

1. **Verify endpoint exists:**

   ```bash
   # Check all API routes
   aws apigatewayv2 get-routes --api-id <api-id>

   # Should show: GET /habits, POST /habits, etc.
   ```

2. **Check handler exists:**

   ```bash
   # Check if Lambda function exists
   aws lambda list-functions \
     | grep -i "habit" | head -5

   # If missing, redeploy
   cd terraform && terraform apply
   ```

3. **Check path parameters:**
   ```
   GET /habits/123          # ✅ Correct
   GET /habit-list          # ❌ Wrong path
   GET /Habits              # ❌ Case sensitive
   ```

---

## Deployment Issues

### "Terraform: Error creating Lambda function"

**Problem:** Deployment fails with Lambda creation error

**Solution:**

```bash
# See detailed error
terraform apply -var="env=prod" 2>&1 | tail -20

# Common causes:
# 1. IAM role doesn't exist
#    → aws iam create-role ... (see IAM section)

# 2. Handler path wrong
#    → Check handler in terraform matches actual file

# 3. Source code ZIP corrupted
#    → Rebuild: make build && make package
```

---

### "DynamoDB table already exists"

**Problem:** Terraform thinks table doesn't exist but it does

**Solution:**

```bash
# Import existing table into Terraform state
terraform import aws_dynamodb_table.self_growth self_growth

# Then:
terraform plan  # Should show "no changes"
terraform apply
```

---

### "API Gateway stage deployment failed"

**Problem:** Deployment succeeds but API not accessible

**Solution:**

```bash
# Verify stage exists
aws apigatewayv2 get-stages --api-id <api-id>

# Verify authorizer configured
aws apigatewayv2 get-authorizers --api-id <api-id>

# Check route integrations
aws apigatewayv2 get-routes --api-id <api-id> \
  | jq '.Items[] | {RouteKey, Target}'

# Re-deploy stage
aws apigatewayv2 create-deployment \
  --api-id <api-id> \
  --stage-name prod
```

---

## Performance Issues

### Slow API Responses

**Problem:** API taking >1 second per request

**Debug Steps:**

```bash
# 1. Check Lambda duration
aws logs insights query \
  --log-group-name /aws/lambda/habit-list \
  --start-time $(date -d '1 hour ago' +%s) \
  --query 'fields @duration | stats avg(@duration), max(@duration)'

# 2. Identify slowest queries
aws logs insights query \
  --log-group-name /aws/lambda/habit-list \
  --query 'fields @duration | filter @duration > 1000'

# 3. Check DynamoDB scan vs query
# Scan = slow (full table)
# Query = fast (uses key)

# 4. Add caching if needed
# See: Caching section in MAINTENANCE.md
```

---

### High AWS Costs

**Problem:** Monthly bill higher than expected

**Analysis:**

```bash
# Break down costs by service
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Expected breakdown:
# Lambda: 50%
# DynamoDB: 30%
# Cognito: 15%
# API Gateway: 3%
# CloudWatch: 2%

# If Lambda >60%:
#   → Reduce invocations or execution time

# If DynamoDB >40%:
#   → Optimize queries or batch operations

# If Cognito >25%:
#   → More users = higher cost, expected
```

---

## Getting Help

### Diagnostic Checklist

Before asking for help, check:

- [ ] Reviewed error message carefully
- [ ] Checked CloudWatch logs `/aws/lambda/...`
- [ ] Used correct API endpoint (check terraform output)
- [ ] JWT token is valid and not expired
- [ ] Input data passes validation
- [ ] AWS credentials configured correctly
- [ ] All dependencies installed (`make install-dev`)
- [ ] Tests pass locally (`make test`)

### Log Investigation Tips

```bash
# Last hour of errors
aws logs tail /aws/lambda/ --follow --since 1h --grep ERROR

# All invocations from specific function
aws logs tail /aws/lambda/habit-create --follow

# Search for pattern
aws logs tail /aws/lambda/ --grep "UnauthorizedError"

# Show slowest invocations
aws logs tail /aws/lambda/habit-list \
  --since 1h | grep "Duration:" | sort -t: -k3 -rn | head
```

### When to Contact Support

- 🟢 AWS credentials issue → Check AWS IAM
- 🟢 Terraform error → Check Terraform docs or error message
- 🟡 Test failures → See test logs
- 🟡 Slow performance → Profile and optimize
- 🔴 Data loss → Restore from backup
- 🔴 Service down → Check AWS status page + run diagnostics

### Resources

- [DEVELOPMENT.md](../DEVELOPMENT.md) — Dev guide
- [ARCHITECTURE.md](../ARCHITECTURE.md) — System design
- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment procedures
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Terraform Docs](https://www.terraform.io/docs)
- [Python boto3 Docs](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

**Last Updated:** March 12, 2026
