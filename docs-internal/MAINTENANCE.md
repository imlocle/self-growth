# Maintenance & Operations

**For: System Administrators & Operators**

**Last Updated:** March 12, 2026

---

## Table of Contents

1. [Regular Maintenance Tasks](#regular-maintenance-tasks)
2. [Performance Tuning](#performance-tuning)
3. [Security Maintenance](#security-maintenance)
4. [Data Management](#data-management)
5. [User Management](#user-management)
6. [Cost Optimization](#cost-optimization)

---

## Regular Maintenance Tasks

### Daily Tasks

#### 1. Monitor Error Rates

```bash
# Check for errors in last 24 hours
aws logs insights query \
  --log-group-name /aws/lambda/ \
  --start-time $(date -d '24 hours ago' +%s) \
  --query 'fields @message | filter @message like /ERROR/ | stats count() as error_count'

# Alert if >100 errors
# Alert if error rate >1%
```

#### 2. Verify API Availability

```bash
# Test health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health)

if [ "$response" != "200" ]; then
  echo "⚠️ API health check failed: $response"
  # Send alert to on-call engineer
fi
```

#### 3. Review CloudWatch Alarms

```bash
# Check for triggered alarms
aws cloudwatch describe-alarms --state-value ALARM

# Expected: Should be 0-1 alarms (investigate if more)
```

### Weekly Tasks

#### 1. Review Performance Metrics

```bash
# Average Lambda duration (target: <500ms)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --statistics Average \
  --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400

# Lambda cold start percentage (target: <5%)
# Calculated from: invocations with @initDuration > 1000ms

# DynamoDB throughput usage (target: <50% of provisioned)
# (Not applicable with PAY_PER_REQUEST mode, but monitor consumed capacity)
```

#### 2. Check Storage Usage

```bash
# DynamoDB table size
aws dynamodb describe-table --table-name self_growth \
  | jq '.Table.TableSizeBytes' | numfmt --to=iec

# Expected: 500MB - 5GB (grow slowly)
# If >10GB, consider archiving old data

# Cognito user count
aws cognito-idp get-user-pool-summary \
  --user-pool-id <pool-id> \
  | jq '.Users'
```

#### 3. Backup Verification

```bash
# Verify latest backup exists
aws dynamodb list-backups --table-name self_growth \
  --query 'BackupSummaries[0]' \
  | jq '.BackupCreationDateTime'

# Verify backup is recoverable (create test restore)
aws dynamodb restore-table-to-point-in-time \
  --source-table-name self_growth \
  --target-table-name self_growth_backup_test \
  --restore-date-time $(date -d '1 day ago' -u +%Y-%m-%dT%H:%M:%S)

# Clean up test restore after verification
aws dynamodb delete-table --table-name self_growth_backup_test
```

#### 4. Security Scan

```bash
# Check CloudWatch Insights for suspicious patterns
aws logs insights query \
  --log-group-name /aws/lambda/ \
  --query 'fields @requestId, user_id | filter @message like /UNAUTHORIZED|FORBIDDEN/ | stats count() by user_id'

# Review for potential abuse patterns
```

### Monthly Tasks

#### 1. Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update non-critical dependencies
pip install --upgrade boto3 dataclasses-json mypy-boto3-*

# Review breaking changes
# Redeploy and test staging

# Do not update boto3 if Lambda layer already includes it
```

#### 2. Cost Review

```bash
# Get AWS billing data
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Expected: ~$20-50/month (adjust for growth)

# Breakdown by service:
# Lambda: 50%
# DynamoDB: 30%
# Cognito: 10-15%
# API Gateway: 3-5%
# CloudWatch: 2-3%
```

#### 3. Documentation Review

```bash
# Update README if changed
# Update ROADMAP with sprint progress
# Document any config changes

git add docs/
git commit -m "Monthly documentation update"
```

#### 4. Infrastructure Audit

```bash
# Compare Terraform state with actual AWS resources
terraform plan

# Should show "No changes"
# If changes detected, investigate drift

# Document any manual AWS changes (should be none)
```

### Quarterly Tasks

#### 1. Security Assessment

```bash
# Run AWS Config compliance checks
aws configservice describe-compliance-by-config-rule \
  --query 'ComplianceByConfigRules[?Compliance.ComplianceType==`NON_COMPLIANT`]'

# Review IAM permissions (least privilege check)
aws iam get-account-authorization-details

# Update security group rules if needed
aws ec2 describe-security-groups
```

#### 2. Performance Plan Review

```bash
# Analyze Lambda execution trends
# Identify slow endpoints
# Plan optimizations

# Review DynamoDB query patterns
# Optimize hot partitions if needed

# Update architecture documentation based on learnings
```

#### 3. Disaster Recovery Drill

```bash
# Test restore procedure
aws dynamodb restore-table-to-point-in-time \
  --source-table-name self_growth \
  --target-table-name self_growth_test \
  --restore-date-time $(date -d '1 day ago' -u +%Y-%m-%dT%H:%M:%S)

# Verify data integrity
# Measure restore time (target: <15 minutes)

# Document findings
# Update runbook if needed

# Clean up
aws dynamodb delete-table --table-name self_growth_test
```

---

## Performance Tuning

### Lambda Optimization

#### Cold Start Reduction

**Current Baseline:** ~3-5s for cold start

**Optimization Opportunities:**

1. **Layer Size Optimization:**

   ```bash
   # Current: ~150MB
   # Target: ~100MB

   # Remove test dependencies from layer
   # Exclude unnecessary packages

   # Rebuild and measure
   du -sh lambda_layer/python/
   ```

2. **Code Optimization:**

   ```python
   # Move imports inside functions that need them
   # Avoid loading large models on startup
   # Use lazy initialization for expensive operations

   # Example: Only import when needed
   def get_analytics(self, habit_id):
       import numpy as np  # Import only when called
       return calculate_analytics(habit_id, np)
   ```

3. **Provisioned Concurrency (if needed):**

   ```bash
   # Reserve execution environments for frequently-used functions
   high_traffic_functions=(
     "habit-list"
     "habit-get"
     "auth-login"
   )

   for func in "${high_traffic_functions[@]}"; do
     aws lambda put-provisioned-concurrency \
       --function-name $func \
       --provisioned-concurrent-executions 10
   done
   ```

### DynamoDB Optimization

#### Query Performance

```python
# Current: ~100-200ms per query

# Optimization checklist:
# ✅ Using correct partition key?
# ✅ Using correct sort key filters?
# ✅ Using GSI for frequently-queried attributes?
# ✅ Limiting result set size (pagination)?

# Example: Efficient query
response = dynamodb.query(
    TableName="self_growth",
    KeyConditionExpression="PK = :pk AND SK BEGINS_WITH :sk",
    ExpressionAttributeValues={
        ":pk": {"S": f"USER#{user_id}"},
        ":sk": {"S": "HABIT#"}
    },
    Limit=20,  # Limit results
    ProjectionExpression="id, title, streak"  # Only get needed columns
)

# Avoid: Full table scans
response = dynamodb.scan(TableName="self_growth")  # ❌ Expensive!
```

#### Partition Key Design

```
Current Design (Optimal):
PK: USER#{user_id}        # Distributes across users
SK: HABIT#{timestamp}     # Allows time-based sorting

Alternative (Worse):
PK: HABIT#{habit_id}      # All habits mixed together
SK: USER#{user_id}        # Doesn't scale well

If seeing hotspots (e.g., popular user has 1M habits):
Consider: Add date shard to SK: HABIT#{YYYY-MM}#{timestamp}
```

### API Gateway Optimization

#### Caching

```bash
# Enable caching for GET requests
aws apigatewayv2 update-stage \
  --api-id <api-id> \
  --stage-name prod \
  --cache-cluster-enabled \
  --cache-cluster-size "0.5"

# Cache-Control headers:
# Cache-Control: max-age=300  # 5 minutes
```

#### Request/Response Compression

```bash
# Already enabled by default in HTTP API
# Gzip compression for bodies >1KB

# Verify:
curl -H "Accept-Encoding: gzip" -I https://api.example.com/habits
# Look for: Content-Encoding: gzip
```

---

## Security Maintenance

### Regular Security Reviews

#### 1. Access Logs Analysis

```bash
# Check for failed auth attempts
aws logs insights query \
  --log-group-name /aws/lambda/auth-login \
  --query 'fields @message | filter @message like /UNAUTHORIZED/ | stats count() by user_id'

# If >10 failed attempts from 1 user: Account takeover attempt
# Action: Block IP, notify user, reset password
```

#### 2. Permission Audit

```bash
# Check who has admin access
aws iam list-users --query 'Users[].UserName'

# Verify no accidental admin permissions
aws iam get-user-policy --user-name <user> --policy-name <policy>

# Remove unnecessary permissions
aws iam delete-user-policy --user-name <user> --policy-name <policy>
```

#### 3. Encryption Verification

```bash
# Verify DynamoDB encryption at rest
aws dynamodb describe-table --table-name self_growth \
  | jq '.Table.SSEDescription'

# Verify Cognito password policy
aws cognito-idp get-user-pool-policy \
  --user-pool-id <pool-id>
```

### Incident Response

#### Security Incident Playbook

```
If Detecting Intrusion/Attack:

1. Isolate (Immediate, <1 min)
   - Block IP at API Gateway
   - Revoke active sessions
   - Enable enhanced logging

2. Investigate (1-5 min)
   - Check logs for affected resources
   - Identify entry point
   - Assess scope of compromise

3. Contain (5-15 min)
   - Reset compromised credentials
   - Update security group rules
   - Enable MFA on account

4. Recover (15-60 min + restore time)
   - Restore from backup if data modified
   - Redeploy with fixes
   - Verify integrity

5. Post-Incident (Day+ after)
   - Conduct root cause analysis
   - Implement preventative measures
   - Update runbook
   - Team retrospective
```

---

## Data Management

### Data Lifecycle

```
Active Data (0-90 days)
└── Full access, high performance

Warm Data (90-365 days)
└── Archived in S3, accessible but slower

Cold Data (>1 year)
└── Deleted per retention policy (optional)
```

### Data Archival

```bash
# Export old data to S3 for archival
aws dynamodb scan \
  --table-name self_growth \
  --expression-attribute-values ':date={S:'2025-01-01'}' \
  --filter-expression 'date_created < :date' \
  | jq '.Items' > archived_data_2025.json

# Upload to S3
aws s3 cp archived_data_2025.json \
  s3://self-growth-backups/archive/2025-01-01/

# Optional: Delete from DynamoDB
# Be careful! Only delete after successful backup verification
```

### Data Retention Policy

```
User data: Retain indefinitely (user responsibility to delete)
Logs: Retain 30 days (configured in CloudWatch)
Backups: Retain 30 days (rolling window)
Archived data: Retain in S3 for 7 years (compliance)
```

---

## User Management

### Bulk User Operations

```bash
# Export all users
aws cognito-idp list-users --user-pool-id <pool-id> \
  --query 'Users[].{Email:Attributes[?Name==`email`].Value, Status:UserStatus}' \
  > users_export.csv

# Reset passwords for users who haven't logged in
aws cognito-idp admin-set-user-password \
  --user-pool-id <pool-id> \
  --username <email> \
  --password TempPassword123! \
  --permanent=false

# Disable inactive users (if needed)
aws cognito-idp admin-disable-user \
  --user-pool-id <pool-id> \
  --username <email>
```

### MFA Enforcement

```bash
# Require MFA for all new users
aws cognito-idp set-user-pool-mfa-config \
  --user-pool-id <pool-id> \
  --mfa-configuration OPTIONAL

# Or: REQUIRED (enforce immediately)
```

---

## Cost Optimization

### AWS Cost Breakdown

```
Monthly costs (estimated for 10,000 users):

Lambda:           $50 (30% of bill)
  Cost drivers: Number of invocations, execution time
  Optimization: Reduce cold starts, optimize execution time

DynamoDB:         $30 (20% of bill)
  Cost drivers: Read/write operations (with PAY_PER_REQUEST)
  Optimization: Efficient queries, batch operations

Cognito:          $25 (16% of bill - variable cost)
  Cost drivers: User count (MAU = Monthly Active Users)
  Optimization: Encourage user retention

API Gateway:      $20 (13% of bill)
  Cost drivers: API calls
  Optimization: Caching, request batching

CloudWatch:       $15 (10% of bill)
  Cost drivers: Logs ingestion
  Optimization: Adjust log retention

CloudFront (CDN): $10 (7% of bill - optional)
  Cost drivers: Data transfer out
  Optimization: Add CloudFront for static assets

Total:            ~$150/month
```

### Cost Reduction Tips

1. **Use S3 Presigned URLs for Large Files**
   - Avoid Lambda memory/timeout costs
   - Direct browser-to-S3 uploads

2. **Enable Query Result Caching**
   - Add CloudFront CDN for read-heavy endpoints
   - Reduces downstream costs

3. **Batch Operations**
   - Use batch read/write instead of individual calls
   - Reduces API calls

4. **Archive Old Data**
   - Move >90 day old data to S3 Glacier
   - Significantly cheaper storage

5. **Optimize Lambda Memory**
   - Profile functions to find optimal memory
   - More memory = faster execution = lower total cost

   ```bash
   # Find optimal memory for habit-list
   for memory in 128 256 512 1024; do
     aws lambda update-function-configuration \
       --function-name habit-list \
       --memory-size $memory

     # Run load test
     # Measure: duration * memory = billed compute
   done
   ```

---

## Scheduled Maintenance

### Monthly Maintenance Window

```
Schedule: 1st Sunday of each month, 2 AM UTC

1. Pre-maintenance (1 hr before)
   - Notify all connected clients
   - Prepare rollback plan
   - Brief on-call team

2. Maintenance (1 hour)
   - Update dependencies
   - Run infrastructure scan
   - Test disaster recovery proc.
   - Verify backups

3. Post-maintenance
   - Smoke tests
   - Performance verification
   - Document any issues
   - Notify all-clear
```

### Update Strategy

```
Development: Weekly (test latest)
Staging: Bi-weekly (before production)
Production: Monthly (tested, stable)

Exception: Security updates deployed immediately
```

---

## Documentation & Runbooks

### Maintenance Log

```bash
# Create maintenance entry
echo "$(date): <action taken> - <results>" >> MAINTENANCE.log

# Example:
# 2026-03-12: Updated boto3 to 1.43.0 - All tests passing
# 2026-03-12: DynamoDB table size: 2.4 GB - Normal growth
# 2026-03-05: Quarterly security audit - No issues found
```

### Runbook Updates

Keep these updated:

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Debug common issues
- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment procedures
- [Incident Response](MAINTENANCE.md#incident-response) — This document

---

**Last Updated:** March 12, 2026
