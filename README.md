# Self Growth

An application to keep track of habits, to-dos, dailies, notes, blog, pro-con list

- Python 3.13
- Terraform

## Set Up

### 1. AWS Credentials

Before deploying, configure AWS credentials:

**Option 1: AWS CLI (Recommended)**

```bash
# Install AWS CLI if not already installed
# macOS: brew install awscli
# Linux: pip install awscli

# Configure credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, region, and output format

# Verify credentials
aws sts get-caller-identity
```

**Option 2: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="us-west-1"  # or your preferred region
```

**Option 3: AWS Profile**

```bash
export AWS_PROFILE=default  # or your profile name
export AWS_REGION="us-west-1"
export AWS_EC2_METADATA_DISABLED=true  # Disable IMDS for local development
```

### 2. Python Environment & Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
```

### 3. Docker (Required for Lambda Layer)

The build process uses Docker to compile Python dependencies for Lambda's Linux environment.

```bash
# Verify Docker is installed and running
docker --version
docker ps
```

## Deployment

### Prerequisites

- AWS credentials configured (see Set Up section)
- Docker installed and running
- Terraform installed

### Deploy to Development

```bash
# Full deployment (builds all Lambda zips + layer, then applies Terraform)
make deploy ENV=dev
```

The Makefile will:

1. Check AWS credentials
2. Build Lambda layer (if requirements.txt changed)
3. Build all Lambda function zips (if source changed)
4. Initialize Terraform with S3 backend
5. Apply Terraform changes

### Deploy to Production

```bash
make deploy ENV=prod
```

### Troubleshooting Deployment

**Error: "no EC2 IMDS role found"**

This means AWS credentials aren't configured. See the AWS Credentials section above.

**Error: "Docker daemon not running"**

Start Docker Desktop or the Docker daemon:

```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

Force Rebuild Layer:

```bash
make rebuild-layer ENV=dev
```

Full Reset:

```bash
make nuke && make deploy ENV=dev
```

## Update Lambda

Build only one Lambda zip:

```bash
make zip-create-todo ENV=dev
```

Deploy only one Lambda (build its zip, then terraform apply):

```bash
make deploy-create-todo ENV=dev
```
