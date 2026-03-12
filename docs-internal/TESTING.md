# Testing Guide

**For: QA Engineers & Developers**

**Last Updated:** March 12, 2026

---

## Table of Contents

1. [Test Organization](#test-organization)
2. [Running Tests](#running-tests)
3. [Writing Tests](#writing-tests)
4. [Test Coverage](#test-coverage)
5. [Continuous Integration](#continuous-integration)
6. [Performance Testing](#performance-testing)

---

## Test Organization

### Test Directory Structure

```
tests/
├── conftest.py                  # Shared fixtures
├── test_models.py               # Model serialization tests
├── test_repositories.py         # Data access layer tests
├── test_services.py             # Business logic tests
├── test_controllers.py          # Request handling tests
├── test_input_sanitization.py   # Security/XSS tests
├── test_utils.py                # Utility function tests
└── test_integration.py          # End-to-end workflow tests
```

### Test Layers

```
Unit Tests (80% of tests)
├── test_models.py          → Individual entity tests
├── test_repositories.py    → CRUD operations, queries
├── test_services.py        → Business logic
├── test_controllers.py     → Request validation
├── test_utils.py           → Helper functions
└── test_input_sanitization.py → Security

Integration Tests (15% of tests)
└── test_integration.py     → Multi-layer workflows

Performance Tests (5% of tests)
└── test_performance.py     → Load & stress testing
```

### Test Coverage by Layer

| Layer        | Tests   | Passing      | Coverage |
| ------------ | ------- | ------------ | -------- |
| Models       | 13      | 13 (100%)    | 100%     |
| Repositories | 12      | 12 (100%)    | 100%     |
| Services     | 12      | 12 (100%)    | 100%     |
| Controllers  | 16      | 11 (69%)     | 85%      |
| Sanitization | 21      | 21 (100%)    | 100%     |
| Utils        | 25      | 21 (84%)     | 90%      |
| Integration  | 12      | 9 (75%)      | 80%      |
| **TOTAL**    | **111** | **99 (89%)** | **92%**  |

---

## Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run all tests with output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test function
pytest tests/test_models.py::test_habit_to_dict

# Run tests matching pattern
pytest -k "habit" -v

# Run with coverage report
pytest --cov=src --cov-report=html

# Run until first failure
pytest -x

# Show print statements
pytest -s
```

### Test Markers

```bash
# Tests are marked with pytest markers
# @pytest.mark.unit       — Unit tests
# @pytest.mark.integration → Integration tests
# @pytest.mark.slow       → Slow tests (>1s)
# @pytest.mark.security   — Security-focused tests

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Show all available markers
pytest --markers
```

### Test Configuration

**pytest.ini:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = -v --tb=short --strict-markers

# Markers
markers =
    unit: Unit tests (single layer)
    integration: Integration/E2E tests
    slow: Slow tests (>1s)
    security: Security-focused tests
```

---

## Writing Tests

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from src.models import Habit

class TestHabit:
    """Test Habit model."""

    def test_habit_creation(self):
        """Test creating a habit instance."""
        # Arrange (setup)
        user_id = "user123"
        title = "Morning Exercise"

        # Act (execute)
        habit = Habit(
            id="habit1",
            user_id=user_id,
            title=title,
            type="BUILD"
        )

        # Assert (verify)
        assert habit.id == "habit1"
        assert habit.user_id == user_id
        assert habit.title == title

    def test_habit_to_dict(self):
        """Test habit serialization to dict."""
        # Arrange
        habit = Habit(..., type=HabitType.BUILD)

        # Act
        result = habit.to_dict()

        # Assert
        assert result["type"] == "BUILD"
        assert "id" in result

    def test_habit_from_dynamo(self):
        """Test deserializing from DynamoDB format."""
        # Arrange
        item = {
            "PK": "HABIT#123",
            "id": "123",
            "title": "Run",
            "type": "BUILD"
        }

        # Act
        habit = Habit.from_dynamo(item)

        # Assert
        assert habit.id == "123"
        assert habit.title == "Run"
```

### Fixtures (Reusable Test Data)

**conftest.py:**

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_habit_repo():
    """Mock habit repository."""
    repo = Mock()
    repo.create.return_value = Habit(id="1", user_id="user1", title="Test")
    repo.get.return_value = Habit(...)
    return repo

@pytest.fixture
def mock_services(mock_habit_repo):
    """Mock all services."""
    return {
        "habit_service": HabitService(mock_habit_repo, ...),
        "access_service": Mock(),
        "auth_service": Mock()
    }

@pytest.fixture
def habit_data():
    """Valid habit creation data."""
    return {
        "title": "Morning Run",
        "type": "BUILD",
        "counter": "DAILY",
        "difficulty": "MEDIUM"
    }
```

**Using fixtures:**

```python
def test_create_habit(mock_services, habit_data):
    """Test habit creation."""
    controller = HabitController(mock_services)
    result = controller.create_habit(habit_data, "user123")
    assert result["title"] == "Morning Run"
```

### Mocking AWS Services

```python
from unittest.mock import Mock, patch
import boto3

@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB service."""
    dynamodb = Mock(spec=boto3.client("dynamodb"))
    dynamodb.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    dynamodb.get_item.return_value = {
        "Item": {
            "id": {"S": "habit1"},
            "title": {"S": "Run"}
        }
    }
    return dynamodb

@pytest.fixture
def mock_cognito():
    """Mock Cognito service."""
    cognito = Mock(spec=boto3.client("cognito-idp"))
    cognito.admin_create_user.return_value = {
        "User": {"Username": "user@example.com"}
    }
    return cognito

def test_with_aws_mock(mock_dynamodb):
    """Test using mocked AWS."""
    repo = HabitRepository(mock_dynamodb)
    # DynamoDB not actually called
```

### Testing Error Cases

```python
def test_create_habit_invalid_title():
    """Test creation with empty title fails."""
    controller = HabitController(services)

    with pytest.raises(ValidationError):
        controller.create_habit({"title": ""}, "user123")

def test_create_habit_unauthorized():
    """Test creation by unauthorized user fails."""
    with pytest.raises(UnauthorizedError):
        service.create("attacker_id", "Run", "BUILD")

def test_create_habit_accepts_normalized_input():
    """Test normalization of input."""
    data = {"title": "  Morning Run  ", "type": "build"}  # lowercase
    result = controller.create_habit(data, "user123")

    assert result["title"] == "Morning Run"
    assert result["type"] == "BUILD"
```

---

## Test Coverage

### Current Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing

# Expected output:
# src/models.py                  95%
# src/controllers.py             87%
# src/services.py                92%
# src/repositories.py            98%
# src/utils/validation.py       100%
# ---
# TOTAL                          92%
```

### Coverage Goals

| Layer        | Current | Target   |
| ------------ | ------- | -------- |
| Models       | 100%    | 100%     |
| Repositories | 98%     | 100%     |
| Services     | 92%     | 95%+     |
| Controllers  | 85%     | 90%+     |
| Utils        | 90%     | 95%+     |
| **TOTAL**    | **92%** | \*\*95%+ |

### Improving Coverage

```bash
# Find uncovered lines
pytest --cov=src --cov-report=html

# Open htmlcov/index.html in browser
# Look for yellow/orange highlighted lines

# Write tests for uncovered branches
# Example: Test error case that's not covered yet
```

---

## Continuous Integration

### GitHub Actions Workflow

**.github/workflows/test.yml:**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: |
          pip install -r src/requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest tests/ --cov=src

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Pre-commit Hooks

**.pre-commit-config.yaml:**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.0.1
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/pylint
    rev: v2.13.0
    hooks:
      - id: pylint
```

**Setup:**

```bash
pip install pre-commit
pre-commit install

# Now hooks run before every commit
```

---

## Performance Testing

### Load Testing

```python
import time
import pytest

@pytest.mark.slow
def test_list_habits_performance():
    """List 1000 habits must complete <1s."""
    service = HabitService(mock_repo)

    # Setup: Create 1000 habits
    habits = [Habit(...) for _ in range(1000)]

    # Time the operation
    start = time.time()
    results = service.list_by_user("user123")
    duration = time.time() - start

    # Assert performance
    assert duration < 1.0, f"Took {duration}s, expected <1s"
    assert len(results) == 1000
```

### Stress Testing

```bash
# Use Apache Bench for API stress testing
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" \
  https://api.example.com/habits

# Results:
# Requests per second: [target: >100]
# Failed requests: [target: 0]
# 50th percentile response time: [target: <200ms]
# 95th percentile response time: [target: <500ms]
```

### Memory Profiling

```python
@pytest.mark.slow
def test_list_habits_memory():
    """Ensure listing habits doesn't leak memory."""
    import tracemalloc

    tracemalloc.start()

    # Initial memory
    baseline = tracemalloc.take_snapshot()

    # Execute operation
    for _ in range(100):
        service.list_by_user("user123")

    # Compare memory
    current = tracemalloc.take_snapshot()
    diff = current.compare_to(baseline, 'lineno')

    # Assert no massive leak
    for stat in diff[:3]:  # Top 3 differences
        assert stat.size < 1_000_000  # <1MB growth
```

---

## Test Maintenance

### Updating Tests

```bash
# If implementation changes but tests are still valid:
pytest --lf  # Run last failed test

# If multiple tests fail due to intentional change:
pytest tests/ --tb=short -q

# Fix them one-by-one
pytest tests/test_models.py::test_specific -v
```

### Debugging Failed Tests

```bash
# Verbose output with traceback
pytest -vv --tb=long

# Drop into debugger
pytest --pdb

# Show print statements
pytest -s

# Show local variables on failure
pytest -l
```

---

## Testing Best Practices

### Do's ✅

- ✅ Write tests before code (TDD)
- ✅ Make tests independent (no shared state)
- ✅ Use descriptive test names
- ✅ Test both happy path and error cases
- ✅ Mock external dependencies (AWS, databases)
- ✅ Keep tests fast (<1s each)
- ✅ Use fixtures for reusable data
- ✅ Verify error messages, not just exceptions

### Don'ts ❌

- ❌ Test implementation details (only behavior)
- ❌ Make tests dependent on order
- ❌ Sleep in tests (99% of the time)
- ❌ Test multiple things in one test
- ❌ Use real AWS services in tests
- ❌ Have tests that randomly pass/fail
- ❌ Test third-party libraries

---

**Last Updated:** March 12, 2026
