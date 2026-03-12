# Development Guide

**A comprehensive guide for developers working on Self-Growth Backend.**

**Last Updated:** March 12, 2026 | **Version:** 1.0

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Project Structure](#project-structure)
3. [Running Tests](#running-tests)
4. [Building Features](#building-features)
5. [Coding Standards](#coding-standards)
6. [Error Handling](#error-handling)
7. [Debugging](#debugging)
8. [Common Commands](#common-commands)
9. [FAQ](#faq)

---

## Local Development Setup

### Prerequisites

- **macOS/Linux** (Windows: use WSL 2)
- **Python 3.13** (pyenv or system)
- **Docker** (for Lambda environment simulation)
- **AWS CLI** v2 (for credential configuration)
- **Terraform** ≥ 1.0
- **Make** (available by default on macOS/Linux)
- **Git**

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/self-growth-backend.git
cd self-growth-backend
```

### Step 2: Set AWS Credentials

```bash
# Configure AWS CLI
aws configure
# Enter:
#   AWS Access Key ID: [your-key]
#   AWS Secret Access Key: [your-secret]
#   Default region: us-west-1
#   Default output format: json

# Verify configuration
aws sts get-caller-identity
# Output:
# {
#   "UserId": "AIDAXXXXXXXXXXXX",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/youruser"
# }
```

### Step 3: Install Python Dependencies

```bash
# Install development dependencies
make install-dev

# This installs:
# - boto3 (AWS SDK)
# - pytest (testing framework)
# - dataclasses-json (serialization)
# - mypy-boto3-* (type hints)
```

### Step 4: Build Lambda Layer

The Lambda layer contains shared dependencies needed by all Lambda functions:

```bash
# Build Docker image for Lambda environment
docker build -t lambda-layer .

# Run container to generate layer
docker run --rm -v $PWD/lambda_layer:/layer lambda-layer:latest

# Result: lambda_layer/python/ contains all dependencies
```

### Step 5: Run Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest --cov=src tests/

# Expected result: 99/111 passing (89%)
```

### Step 6: Start Local Development

```bash
# Verify everything works
python -m pytest tests/ -k "test_habit" --tb=short

# Ready to develop!
```

---

## Project Structure

```
self-growth-backend/
├── src/                              # Main application code
│   ├── __init__.py
│   ├── requirements.txt               # Python dependencies
│   │
│   ├── aws/                          # AWS service wrappers (Cognito, DynamoDB)
│   │   ├── __init__.py
│   │   ├── cognito_service.py        # User authentication (signup, login)
│   │   └── dynamodb_service.py       # Database operations
│   │
│   ├── controllers/                  # Request handlers (validation, routing)
│   │   ├── __init__.py
│   │   ├── base_controller.py        # Base class with utilities
│   │   ├── auth_controller.py        # Authentication endpoints
│   │   ├── habit_controller.py       # Habit CRUD operations
│   │   ├── todo_controller.py        # Todo CRUD operations
│   │   ├── blog_post_controller.py   # Blog post operations
│   │   ├── household_controller.py   # Household management
│   │   └── ...
│   │
│   ├── handlers/                     # Lambda entry points
│   │   ├── __init__.py
│   │   ├── base_handler.py           # Base handler class
│   │   ├── auth/
│   │   │   ├── signup.py             # POST /auth/signup
│   │   │   ├── login.py              # POST /auth/login
│   │   │   ├── refresh.py            # POST /auth/refresh
│   │   │   └── confirm.py            # POST /auth/confirm
│   │   ├── habits/
│   │   │   ├── create.py             # POST /habits
│   │   │   ├── get.py                # GET /habits/{id}
│   │   │   ├── list.py               # GET /habits
│   │   │   ├── update.py             # PUT /habits/{id}
│   │   │   ├── delete.py             # DELETE /habits/{id}
│   │   │   └── ...
│   │   ├── todos/
│   │   ├── blog_posts/
│   │   └── ...
│   │
│   ├── services/                     # Business logic (features)
│   │   ├── __init__.py
│   │   ├── auth_service.py           # Authentication workflows
│   │   ├── habit_service.py          # Habit logic
│   │   ├── habit_analytics_service.py # Streak calculation
│   │   ├── todo_service.py           # Todo logic
│   │   ├── blog_post_service.py      # Blog post logic
│   │   ├── household_service.py      # Household logic
│   │   ├── access_service.py         # Authorization checks
│   │   └── ...
│   │
│   ├── repositories/                 # Data persistence layer
│   │   ├── __init__.py
│   │   ├── habit_repository.py       # Habit CRUD (DynamoDB)
│   │   ├── todo_repository.py        # Todo CRUD (DynamoDB)
│   │   ├── blog_post_repository.py   # Blog post CRUD
│   │   ├── household_repository.py   # Household CRUD
│   │   └── ...
│   │
│   ├── models/                       # Domain entities (dataclasses)
│   │   ├── __init__.py
│   │   ├── base_model.py             # Base model with serialization
│   │   ├── enum.py                   # Enums (HabitType, Status, etc.)
│   │   ├── errors.py                 # Custom exceptions
│   │   ├── habit.py                  # Habit entity
│   │   ├── todo.py                   # Todo entity
│   │   ├── blog_post.py              # BlogPost entity
│   │   ├── user_profile.py           # User entity
│   │   ├── household.py              # Household entity
│   │   └── ...
│   │
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── validation.py             # Input validation & sanitization
│       ├── errors.py                 # Error response models
│       ├── request_context.py        # Request context extraction
│       └── response_utils.py         # Response formatting
│
├── tests/                            # Test suite (111 tests, 89% passing)
│   ├── conftest.py                   # Pytest fixtures and configuration
│   ├── test_models.py                # Model serialization tests
│   ├── test_repositories.py          # Repository/persistence tests
│   ├── test_services.py              # Service/business logic tests
│   ├── test_controllers.py           # Controller/request validation tests
│   ├── test_utils.py                 # Utility function tests
│   ├── test_integration.py           # End-to-end workflow tests
│   └── test_input_sanitization.py    # Security/XSS prevention tests
│
├── terraform/                        # Infrastructure as Code
│   ├── main.tf                       # Main configuration
│   ├── variables.tf                  # Variable definitions
│   ├── outputs.tf                    # Output values
│   ├── backend.auto.hcl              # Remote state (Terraform Cloud)
│   ├── backend.tf                    # Backend configuration
│   └── modules/
│       ├── cognito/                  # Cognito user pool setup
│       ├── dynamodb/                 # DynamoDB table setup
│       ├── lambda/                   # Lambda functions, layers, IAM
│       └── api/                      # API Gateway setup
│
├── lambda_layer/
│   └── python/                       # Shared Lambda dependencies (compiled)
│
├── docs/                             # Public documentation
│   ├── INDEX.md                      # Documentation navigation
│   ├── README.md                     # Project overview
│   ├── ARCHITECTURE.md               # System architecture
│   ├── DEVELOPMENT.md                # This file
│   ├── BUGS.md                       # Known issues
│   ├── ROADMAP.md                    # Future features
│   └── api-reference.md              # API documentation
│
├── docs-internal/                    # Internal documentation
│   ├── CODEBASE_STRUCTURE.md         # Codebase deep dive
│   ├── DEPLOYMENT.md                 # Deployment procedures
│   ├── MAINTENANCE.md                # Maintenance tasks
│   ├── TESTING.md                    # Testing strategies
│   └── TROUBLESHOOTING.md            # Debugging guide
│
├── Makefile                          # Development commands
├── pytest.ini                        # Pytest configuration
├── README.md                         # Root README
├── requirements.txt                  # Root-level dependencies
└── run_tests.sh                      # Test runner script

```

---

## Running Tests

### Test Organization

Tests are organized by layer:

| Layer          | File                                           | Tests | Status    |
| -------------- | ---------------------------------------------- | ----- | --------- |
| Models         | `test_models.py`                               | 13    | ✅ 100%   |
| Repositories   | `test_repositories.py`                         | 12    | ✅ 100%   |
| Services       | `test_services.py`                             | 12    | ✅ 100%   |
| Controllers    | `test_controllers.py`                          | 16    | 🟡 69%    |
| Integration    | `test_integration.py`                          | 12    | 🟡 75%    |
| Utils/Security | `test_utils.py` + `test_input_sanitization.py` | 46    | 🟡 91%    |
| **TOTAL**      | —                                              | 111   | **99 ✅** |

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_models.py

# Run specific test function
pytest tests/test_models.py::test_habit_to_dict

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src

# Run tests matching pattern
pytest -k "habit" -v

# Stop on first failure
pytest -x

# Run with detailed traceback
pytest --tb=long

# Run in parallel (multiple workers)
pytest -n 4
```

### Understanding Test Failures

Test failures are typically in:

1. **Controllers** — Missing request body data in test setup
2. **Integration** — AccessService constructor parameter mismatches
3. **Utils** — Some edge cases not fully covered

**To fix a failing test:**

```bash
# Run the specific test with traceback
pytest tests/test_controllers.py::test_habit_create -v --tb=short

# Read the error message to understand what's wrong
# Check if mocks are set up correctly
# Check parameter names match actual implementation
```

---

## Building Features

### 1. Adding a New Endpoint

**Example: Create a "Get Today's Habits" endpoint**

#### Step 1: Create Handler (`src/handlers/habits/get_today.py`)

```python
import json
from src.utils.request_context import get_request_context
from src.controllers.habit_controller import HabitController

def lambda_handler(event, context):
    try:
        # Extract user context from JWT token
        user_id = get_request_context(event)["user_id"]

        # Get today's date from query parameter
        today = event.get("queryStringParameters", {}).get("date")

        # Call controller
        controller = HabitController()
        habits = controller.get_today_habits(user_id, today)

        # Return success response
        return {
            "statusCode": 200,
            "body": json.dumps(habits)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
```

#### Step 2: Add Controller Method (`src/controllers/habit_controller.py`)

```python
def get_today_habits(self, user_id: str, date: str) -> dict:
    """Get all habits for today with their event status."""
    # Validate date format (YYYY-MM-DD)
    validated = validate_habit_date(date)

    # Call service
    habits = self.habit_service.get_today_habits(user_id, validated)

    # Return formatted response
    return [habit.to_dict() for habit in habits]
```

#### Step 3: Add Service Method (`src/services/habit_service.py`)

```python
def get_today_habits(self, user_id: str, date: str) -> list:
    """Retrieve all habits for a specific date."""
    # Check authorization
    self.access_service.check_ownership(user_id)

    # Get all active habits
    habits = self.habit_repo.get_by_user(user_id)

    # Filter to active habits
    active_habits = [h for h in habits if h.status == HabitStatus.ACTIVE]

    # Get today's events
    today_events = self.habit_event_repo.get_by_date(user_id, date)

    # Enrich habits with today's status
    for habit in active_habits:
        habit.today_completed = any(
            e.habit_id == habit.id for e in today_events
        )

    return active_habits
```

#### Step 4: Add Repository Method (if needed)

```python
def get_by_user(self, user_id: str) -> list:
    """Get all habits for a user."""
    response = self.dynamodb.query(
        "self_growth",
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": f"USER#{user_id}"}
    )
    return [Habit.from_dynamo(item) for item in response.get("Items", [])]
```

#### Step 5: Add Tests

```python
# tests/test_controllers.py
def test_get_today_habits(mock_habit_service):
    controller = HabitController(mock_habit_service)
    result = controller.get_today_habits("user123", "2026-03-12")
    assert len(result) > 0
    assert "today_completed" in result[0]

# tests/test_services.py
def test_get_today_habits_service(mock_habit_repo, mock_habit_event_repo):
    service = HabitService(mock_habit_repo, mock_habit_event_repo)
    habits = service.get_today_habits("user123", "2026-03-12")
    assert len(habits) > 0
```

#### Step 6: Register in Terraform

```hcl
# terraform/modules/lambda/main.tf

resource "aws_lambda_function" "habit_get_today" {
  filename            = data.archive_file.code.output_path
  function_name       = "habit-get-today"
  role               = aws_iam_role.lambda_role.arn
  handler            = "src/handlers/habits/get_today.lambda_handler"
  runtime            = "python3.13"
  source_code_hash   = data.archive_file.code.output_base64sha256
  layers             = [aws_lambda_layer_version.dependencies.arn]
  timeout            = 30
  memory_size        = 256
}
```

---

## Coding Standards

### Python Style

- **Line Length:** 100 characters max
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Group by stdlib, third-party, local (use isort)
- **Type Hints:** Use for function arguments and returns

**Example:**

```python
from typing import Optional, List
from dataclasses import dataclass
from src.models import Habit

@dataclass
class HabitService:
    habit_repo: "HabitRepository"

    def create_habit(
        self,
        user_id: str,
        title: str,
        habit_type: str
    ) -> Habit:
        """Create a new habit for a user.

        Args:
            user_id: The user creating the habit
            title: Habit title (1-200 chars)
            habit_type: "BUILD" or "QUIT"

        Returns:
            The created Habit object

        Raises:
            ValidationError: If input is invalid
            UnauthorizedError: If user lacks permission
        """
        # Validate inputs
        if not title or len(title) > 200:
            raise ValidationError("Title must be 1-200 characters")

        # Create entity
        habit = Habit(id=uuid4(), user_id=user_id, title=title)

        # Persist
        return self.habit_repo.create(habit)
```

### Naming Conventions

| Type              | Convention          | Example                          |
| ----------------- | ------------------- | -------------------------------- |
| Classes           | PascalCase          | `HabitService`, `UserRepository` |
| Functions/Methods | snake_case          | `create_habit`, `get_by_user`    |
| Constants         | UPPER_SNAKE_CASE    | `MAX_TITLE_LENGTH = 200`         |
| Private Methods   | `_snake_case`       | `_validate_input`                |
| Models            | Singular noun       | `Habit`, not `Habits`            |
| Repositories      | `{Model}Repository` | `HabitRepository`                |
| Services          | `{Domain}Service`   | `HabitService`                   |

### Documentation

Every public function needs:

```python
def create_habit(self, user_id: str, title: str) -> Habit:
    """Create a new habit for a user.

    Args:
        user_id: The user creating the habit
        title: Habit title (1-200 characters)

    Returns:
        The created Habit object

    Raises:
        ValidationError: If title is invalid
        UnauthorizedError: If user not authenticated
    """
    pass
```

---

## Error Handling

### Error Types

**Custom Exceptions in `src/models/errors.py`:**

```python
class ValidationError(Exception):
    """Input validation failed."""
    pass

class UnauthorizedError(Exception):
    """User not authenticated or lacks permission."""
    pass

class NotFoundError(Exception):
    """Requested resource not found."""
    pass

class ConflictError(Exception):
    """Request conflicts with existing data."""
    pass
```

### Error Responses

Controllers convert exceptions to HTTP responses:

```python
def create_habit(self, data: dict, user_id: str) -> dict:
    try:
        validated = validate_habit_data(data)
        habit = self.habit_service.create(user_id, **validated)
        return habit.to_dict()

    except ValidationError as e:
        raise APIException(400, "INVALID_INPUT", str(e))

    except UnauthorizedError as e:
        raise APIException(403, "FORBIDDEN", "You don't have permission")

    except Exception as e:
        # Log the error for debugging
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise APIException(500, "INTERNAL_ERROR", "An error occurred")
```

### HTTP Status Codes

| Code | Use Case     | Example                  |
| ---- | ------------ | ------------------------ |
| 200  | Success      | GET /habits returns 200  |
| 201  | Created      | POST /habits returns 201 |
| 400  | Bad request  | Missing required field   |
| 401  | Unauthorized | Missing/invalid JWT      |
| 403  | Forbidden    | User lacks permission    |
| 404  | Not found    | Habit doesn't exist      |
| 409  | Conflict     | Email already registered |
| 500  | Server error | Database unreachable     |

---

## Debugging

### Local Testing with Mocks

```python
# Create mock AWS services
@pytest.fixture
def mock_dynamodb():
    return Mock(spec=DynamoDBService)

@pytest.fixture
def mock_cognito():
    return Mock(spec=CognitoService)

def test_habit_creation(mock_dynamodb, mock_cognito):
    # Arrange
    mock_dynamodb.put.return_value = {"id": "123"}

    # Act
    repo = HabitRepository(mock_dynamodb)
    result = repo.create(habit)

    # Assert
    assert result["id"] == "123"
    mock_dynamodb.put.assert_called_once()
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def create_habit(self, user_id: str, title: str):
    logger.info(f"Creating habit for user {user_id}")
    try:
        habit = Habit(...)
        logger.debug(f"Habit object created: {habit}")
        return self.repo.create(habit)
    except Exception as e:
        logger.error(f"Error creating habit: {e}", exc_info=True)
        raise
```

### CloudWatch Logs

```bash
# View latest logs for a Lambda function
aws logs tail /aws/lambda/habit-create --follow

# View logs for specific time period
aws logs tail /aws/lambda/habit-create --since 1h

# Search for errors
aws logs tail /aws/lambda/habit-create --grep ERROR
```

---

## Common Commands

```bash
# Installation & Setup
make install-dev          # Install development dependencies
make install              # Install production dependencies

# Testing
make test                 # Run all tests (89% passing expected)
pytest -v               # Verbose test output
pytest -k habit         # Run tests matching pattern
pytest --cov=src        # Show code coverage

# Linting & Formatting
make lint                # Run pylint
make format              # Format code with black
make check               # Run all checks

# Building
make build               # Build Lambda layer
make package             # Package for deployment

# Deployment
make deploy              # Deploy to staging
make deploy-prod         # Deploy to production

# Utilities
make clean               # Remove build artifacts
make help                # Show all commands
```

---

## FAQ

### Q: How do I add a new model entity?

**A:** Create a new file in `src/models/`, define the dataclass, implement `to_dict()` and `from_dynamo()` methods, and add it to `__init__.py`.

### Q: How do I run a specific test?

**A:** `pytest tests/test_habits.py::test_create_habit -v`

### Q: How do I debug a failing Lambda function?

**A:** Enable debug logging in handler, check CloudWatch logs with `aws logs tail`, or run locally with mocked AWS services.

### Q: What's the difference between repositories and services?

**A:** Repository = data access (CRUD). Service = business logic (validation, authorization, calculations).

### Q: How do I add authorization to a new endpoint?

**A:** Call `self.access_service.check_permission(user_id, resource_id)` in the service layer.

### Q: How do I prevent XSS attacks?

**A:** Use `sanitize_string()` in validation functions. All input is automatically sanitized.

### Q: Where do I find API examples?

**A:** See [api-reference.md](api-reference.md) for cURL, Python, and JavaScript examples.

### Q: How do I test locally without AWS credentials?

**A:** Use pytest mocks to simulate DynamoDB and Cognito. See `tests/conftest.py` for fixtures.

### Q: What's the deployment process?

**A:** `make test` → `make build` → `make deploy` → verify in AWS Console → check CloudWatch logs.

---

**Next Steps:**

- Try building a small feature following the guide above
- Run tests to verify your changes
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for deep technical details
- See [docs-internal/TESTING.md](../docs-internal/TESTING.md) for advanced testing strategies

---

**Last Updated:** March 12, 2026
