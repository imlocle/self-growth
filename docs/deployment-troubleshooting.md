# Deployment Troubleshooting

## Common Deployment Errors

### 1. AWS Credentials Error

**Error Message:**

```
Error: failed to refresh cached credentials, no EC2 IMDS role found
```

**Cause:** AWS credentials are not configured or Terraform is trying to use EC2 instance metadata (IMDS) when running locally.

**Solution:**

Choose one of these methods:

**Method 1: AWS CLI Profile (Recommended)**

```bash
# Configure AWS CLI
aws configure

# Set environment variables
export AWS_PROFILE=default
export AWS_REGION=us-west-1
export AWS_EC2_METADATA_DISABLED=true

# Verify
aws sts get-caller-identity

# Deploy
make deploy ENV=dev
```

**Method 2: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-west-1"

# Deploy
make deploy ENV=dev
```

**Method 3: Named Profile**

```bash
# If you have multiple AWS profiles
export AWS_PROFILE=my-profile-name
export AWS_REGION=us-west-1

# Deploy
make deploy ENV=dev
```

---

### 2. Docker Not Running

**Error Message:**

```
Cannot connect to the Docker daemon
```

**Cause:** Docker daemon is not running.

**Solution:**

**macOS:**

```bash
open -a Docker
# Wait for Docker Desktop to start
```

**Linux:**

```bash
sudo systemctl start docker
sudo systemctl enable docker  # Start on boot
```

**Verify:**

```bash
docker ps
```

---

### 3. Terraform State Lock

**Error Message:**

```
Error: Error acquiring the state lock
```

**Cause:** Another Terraform process is running or a previous run didn't release the lock.

**Solution:**

**Option 1: Wait**
If another deployment is running, wait for it to complete.

**Option 2: Force Unlock (Dangerous)**

```bash
cd terraform
terraform force-unlock <LOCK_ID>
```

⚠️ Only use this if you're certain no other process is running!

---

### 4. S3 Backend Bucket Doesn't Exist

**Error Message:**

```
Error: Failed to get existing workspaces: S3 bucket does not exist
```

**Cause:** The Terraform state bucket hasn't been created yet.

**Solution:**

Create the S3 bucket manually:

```bash
aws s3 mb s3://self-growth-terraform-state-bucket --region us-west-1
```

Or use the AWS Console:

1. Go to S3
2. Create bucket: `self-growth-terraform-state-bucket`
3. Region: `us-west-1`
4. Enable versioning (recommended)

---

### 5. Lambda Layer Build Fails

**Error Message:**

```
Error: Could not find a version that satisfies the requirement
```

**Cause:** Python dependency conflict or network issue.

**Solution:**

**Rebuild the layer:**

```bash
make rebuild-layer ENV=dev
```

**Check Docker platform:**

```bash
# Ensure using linux/amd64 platform
docker run --rm --platform linux/amd64 public.ecr.aws/sam/build-python3.13 python --version
```

**Clear Docker cache:**

```bash
docker system prune -a
make rebuild-layer ENV=dev
```

---

### 6. Terraform Provider Download Fails

**Error Message:**

```
Error: Failed to install provider
```

**Cause:** Network issue or provider registry unavailable.

**Solution:**

**Retry:**

```bash
cd terraform
terraform init -upgrade
```

**Use mirror (if in restricted network):**

```bash
# Add to ~/.terraformrc
provider_installation {
  network_mirror {
    url = "https://terraform-mirror.example.com/"
  }
}
```

---

### 7. Lambda Function Already Exists

**Error Message:**

```
Error: error creating Lambda Function: ResourceConflictException
```

**Cause:** Lambda function already exists (possibly from manual creation).

**Solution:**

**Import existing resource:**

```bash
cd terraform
terraform import module.lambda.module.create_todo.aws_lambda_function.this self-growth-create-todo-dev
```

**Or delete and recreate:**

```bash
aws lambda delete-function --function-name self-growth-create-todo-dev
make deploy ENV=dev
```

---

### 8. API Gateway Deployment Fails

**Error Message:**

```
Error: error creating API Gateway v2 deployment
```

**Cause:** API Gateway resource conflict or invalid configuration.

**Solution:**

**Check existing APIs:**

```bash
aws apigatewayv2 get-apis
```

**Delete conflicting API:**

```bash
aws apigatewayv2 delete-api --api-id <api-id>
```

**Redeploy:**

```bash
make deploy ENV=dev
```

---

### 9. DynamoDB Table Already Exists

**Error Message:**

```
Error: error creating DynamoDB Table: ResourceInUseException
```

**Cause:** Table already exists.

**Solution:**

**Import existing table:**

```bash
cd terraform
terraform import module.dynamodb.aws_dynamodb_table.self_growth_table self-growth-table-dev
```

**Or delete and recreate (⚠️ DATA LOSS):**

```bash
aws dynamodb delete-table --table-name self-growth-table-dev
make deploy ENV=dev
```

---

### 10. Insufficient IAM Permissions

**Error Message:**

```
Error: AccessDeniedException: User is not authorized to perform: lambda:CreateFunction
```

**Cause:** AWS credentials don't have sufficient permissions.

**Solution:**

**Check current user:**

```bash
aws sts get-caller-identity
```

**Required IAM permissions:**

- Lambda: Full access
- API Gateway: Full access
- DynamoDB: Full access
- Cognito: Full access
- CloudWatch: Logs and metrics
- IAM: Create/attach roles and policies
- S3: State bucket access

**Attach policy to user:**

```bash
aws iam attach-user-policy \
  --user-name your-username \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

Or create a custom policy with minimum required permissions.

---

## Verification Steps

### 1. Verify AWS Credentials

```bash
aws sts get-caller-identity
```

Expected output:

```json
{
  "UserId": "AIDAI...",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

### 2. Verify Docker

```bash
docker --version
docker ps
```

### 3. Verify Terraform

```bash
cd terraform
terraform version
terraform validate
```

### 4. Verify Python Environment

```bash
source .venv/bin/activate
python --version  # Should be 3.13+
pip list | grep boto3
```

---

## Clean Slate Deployment

If everything is broken, start fresh:

```bash
# 1. Clean local artifacts
make nuke

# 2. Verify AWS credentials
aws sts get-caller-identity

# 3. Ensure Docker is running
docker ps

# 4. Deploy from scratch
make deploy ENV=dev
```

---

## Getting Help

### Check Logs

**Terraform logs:**

```bash
cd terraform
terraform plan  # Dry run to see what will change
```

**CloudWatch logs:**

```bash
aws logs tail /aws/lambda/self-growth-create-todo-dev --follow
```

**API Gateway logs:**

```bash
aws logs tail /aws/apigateway/self-growth-dev --follow
```

### Debug Mode

**Terraform debug:**

```bash
export TF_LOG=DEBUG
cd terraform
terraform apply -var="environment=dev"
```

**AWS CLI debug:**

```bash
aws lambda list-functions --debug
```

---

## Contact

If you encounter an issue not covered here, check:

1. [AWS Service Health Dashboard](https://status.aws.amazon.com/)
2. [Terraform AWS Provider Issues](https://github.com/hashicorp/terraform-provider-aws/issues)
3. Project documentation in `docs/`
