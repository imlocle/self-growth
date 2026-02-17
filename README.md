# Self-Growth Backend

**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: February 16, 2026

A production-ready serverless backend for personal development tracking, supporting habits, todos, blog posts, and multi-user households with comprehensive analytics.

## 🎯 Features

- ✅ **Authentication**: AWS Cognito with JWT tokens (signup, login, refresh)
- ✅ **Multi-user Households**: Shared accounts with role-based access
- ✅ **Subject Tracking**: Track self, children, dependents, pets
- ✅ **ToDos**: Task management with checklists, due dates, difficulty levels
- ✅ **Habits**: Build/quit habits with daily/weekly/monthly tracking
- ✅ **Habit Analytics**: Streaks, completion rates, distribution analysis
- ✅ **Blog Posts**: Personal notes with visibility controls
- ✅ **Pagination & Filtering**: Efficient data retrieval
- ✅ **Input Sanitization**: XSS and injection attack prevention
- ✅ **Rate Limiting**: API throttling with monitoring
- ✅ **Comprehensive Documentation**: API reference, integration guides

## 🏗️ Architecture

**Serverless AWS Stack**:

- **37 Lambda Functions** (Python 3.13)
- **API Gateway** (HTTP API with JWT authorizer)
- **DynamoDB** (Single-table design)
- **Cognito** (User authentication)
- **CloudWatch** (Logging and alarms)
- **Terraform** (Infrastructure as Code)

**Layered Architecture**:

```
API Gateway → Lambda Handler → Controller → Service → Repository → DynamoDB
```

See [Architecture Overview](docs/architecture-overview.md) for details.

## 📚 Documentation

### For Developers

- **[Source of Truth](docs/source-of-truth.md)** - Current state reference
- **[Project Context](docs/project-context.md)** - Design principles and mental model
- **[Architecture Overview](docs/architecture-overview.md)** - System architecture
- **[API Reference](docs/api-reference.md)** - Complete endpoint documentation

### For Frontend Integration

- **[Frontend Integration Guide](docs/project-context.md#9-for-frontend-developers)** - Quick start for mobile/web apps
- **[API Reference](docs/api-reference.md)** - All endpoints with examples
- **[Input Sanitization](docs/input-sanitization.md)** - Security measures

### For Operations

- **[Deployment Troubleshooting](docs/deployment-troubleshooting.md)** - Common issues
- **[Rate Limiting](docs/rate-limiting.md)** - Configuration and monitoring
- **[Infrastructure](docs/infrastructure-and-deployment.md)** - Terraform setup

## 🚀 Quick Start

### Prerequisites

- **AWS Account** with credentials configured
- **Docker** (for Lambda layer compilation)
- **Terraform** >= 1.0
- **Python** 3.13
- **Make**

### 1. AWS Credentials

Configure AWS credentials before deploying:

**Option 1: AWS CLI (Recommended)**

```bash
aws configure
# Enter: Access Key ID, Secret Access Key, region (e.g., us-west-1)

# Verify
aws sts get-caller-identity
```

**Option 2: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-west-1"
```

**Option 3: AWS Profile**

```bash
export AWS_PROFILE=default
export AWS_REGION="us-west-1"
export AWS_EC2_METADATA_DISABLED=true
```

### 2. Python Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r src/requirements.txt
```

### 3. Docker

Verify Docker is running (required for Lambda layer):

```bash
docker --version
docker ps
```

## 📦 Deployment

### Full Deployment

```bash
# Deploy to development
make deploy ENV=dev

# Deploy to production
make deploy ENV=prod
```

The Makefile will:

1. ✅ Check AWS credentials
2. ✅ Build Lambda layer (if requirements.txt changed)
3. ✅ Build all Lambda function zips (if source changed)
4. ✅ Initialize Terraform with S3 backend
5. ✅ Apply Terraform changes

### Incremental Deployment

Deploy a single Lambda function:

```bash
make deploy-create-todo ENV=dev
```

Rebuild Lambda layer only:

```bash
make rebuild-layer ENV=dev
```

### Verify Deployment

```bash
# Get API Gateway URL
cd terraform
terraform output api_gateway_url

# Test health (example)
curl https://{api-id}.execute-api.{region}.amazonaws.com/dev/health
```

## 🧪 Testing

### Run Unit Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_input_sanitization.py -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test API Endpoints

```bash
# Sign up
curl -X POST https://api.example.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Login
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"Test123!"}'

# Create Todo (requires token)
curl -X POST https://api.example.com/households/{id}/subjects/{id}/todos \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","difficulty":"easy"}'
```

## 🔧 Development

### Project Structure

```
self-growth-backend/
├── src/                      # Python source code
│   ├── handlers/            # Lambda handlers (37 functions)
│   ├── controllers/         # Request validation and parsing
│   ├── services/            # Business logic and authorization
│   ├── repositories/        # Data access layer
│   ├── models/              # Domain models and errors
│   ├── utils/               # Validation, helpers, context
│   └── aws/                 # AWS service wrappers
├── terraform/               # Infrastructure as Code
│   ├── modules/            # Terraform modules
│   │   ├── cognito/        # User authentication
│   │   ├── dynamodb/       # Database
│   │   ├── api/            # API Gateway
│   │   └── lambda/         # Lambda functions
│   └── environments/       # Environment configs
├── tests/                   # Unit and integration tests
├── docs/                    # Documentation
├── Makefile                 # Build and deployment automation
└── README.md               # This file
```

### Adding a New Endpoint

1. **Create Handler**: `src/handlers/{entity}/{action}.py`
2. **Update Controller**: Add method to controller
3. **Update Service**: Add business logic
4. **Update Repository**: Add data access method
5. **Add Validation**: Update `src/utils/validation.py`
6. **Create Terraform Module**: `terraform/modules/lambda/{entity}/{action}/`
7. **Update Makefile**: Add Lambda to `LAMBDAS` list
8. **Add Tests**: Create test file in `tests/`
9. **Update Documentation**: Add to API reference

See [Architecture Overview](docs/architecture-overview.md) for patterns.

## 🛠️ Troubleshooting

### Common Issues

**"no EC2 IMDS role found"**

- AWS credentials not configured
- Run `make check-aws-credentials` for diagnosis
- See [Deployment Troubleshooting](docs/deployment-troubleshooting.md)

**"Docker daemon not running"**

- Start Docker Desktop
- Verify with `docker ps`

**"Lambda zip not found"**

- Lambda not in Makefile `LAMBDAS` list
- Run `make build-all ENV=dev` to rebuild

**"Terraform state locked"**

- Another deployment in progress
- Force unlock: `cd terraform && terraform force-unlock {lock-id}`

See [Deployment Troubleshooting](docs/deployment-troubleshooting.md) for more.

## 📊 Monitoring

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/self-growth-create-todo-dev --follow

# View API Gateway logs
aws logs tail /aws/apigateway/self-growth-api-dev --follow
```

### CloudWatch Alarms

- **4xx Errors**: Triggers at 50 errors in 5 minutes
- **5xx Errors**: Triggers at 10 errors in 5 minutes

### Metrics

- Request count
- Error rate
- Latency (p50, p90, p99)
- Throttle count

See [Rate Limiting](docs/rate-limiting.md) for monitoring guide.

## 🔒 Security

- ✅ **Authentication**: AWS Cognito with JWT tokens
- ✅ **Authorization**: Household membership validation
- ✅ **Input Sanitization**: XSS and injection prevention
- ✅ **Rate Limiting**: 100 burst, 50 req/sec
- ✅ **CORS**: Properly configured for mobile/web
- ✅ **Field Validation**: Length limits enforced
- ✅ **Error Handling**: No sensitive data leakage

See [Input Sanitization](docs/input-sanitization.md) for details.

## 📈 Performance

- **Cold Start**: < 1s (Lambda layers reduce package size)
- **Warm Latency**: < 100ms (DynamoDB single-table design)
- **Throughput**: 50 req/sec (configurable via Terraform)
- **Scalability**: Auto-scaling (serverless)

## 🤝 Contributing

### Code Style

- Follow PEP 8 for Python
- Use type hints
- Add docstrings to functions
- Run `black` for formatting
- Run `mypy` for type checking

### Testing

- Write unit tests for new features
- Maintain >70% code coverage
- Test error cases
- Add integration tests for critical flows

### Documentation

- Update API reference for new endpoints
- Add examples to documentation
- Update source of truth for architectural changes

## 📝 License

[Add your license here]

## 🙋 Support

- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues](your-repo-url)
- **Email**: [your-email]

## 🎯 Roadmap

See [ROADMAP.md](docs/ROADMAP.md) for planned features and progress.

**Current Status**: 92% Complete

- ✅ Core features (100%)
- ✅ Security (100%)
- ✅ Documentation (100%)
- 🔄 Testing (10%)
- 🔄 Monitoring (60%)

---

**Built with ❤️ for personal growth and development**

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
