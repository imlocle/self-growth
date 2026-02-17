# Testing Guide

**Last Updated**: February 16, 2026  
**Status**: Complete  
**Test Coverage**: 70%+

This guide explains how to run and write tests for the Self-Growth backend.

---

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Coverage](#test-coverage)
6. [Continuous Integration](#continuous-integration)
7. [Best Practices](#best-practices)

---

## Overview

The Self-Growth backend uses **pytest** as the testing framework with comprehensive unit and integration tests covering:

- **Models**: Domain entity serialization and validation
- **Repositories**: Data access layer with DynamoDB
- **Services**: Business logic and authorization
- **Controllers**: Request validation and parsing
- **Utilities**: Helper functions and request context
- **Integration**: End-to-end flows

### Test Philosophy

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test multiple components working together
- **Mocking**: Mock external dependencies (AWS services)
- **Fast execution**: Tests should run quickly (< 5 seconds total)
- **Deterministic**: Tests should produce consistent results

---

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_models.py              # Domain model tests
├── test_repositories.py        # Repository layer tests
├── test_services.py            # Service layer tests
├── test_controllers.py         # Controller layer tests
├── test_utils.py               # Utility function tests
├── test_input_sanitization.py  # Security/validation tests
└── test_integration.py         # End-to-end integration tests
```

### Test Files

| File                         | Purpose                                            | Test Count |
| ---------------------------- | -------------------------------------------------- | ---------- |
| `conftest.py`                | Shared fixtures (users, households, events, mocks) | N/A        |
| `test_models.py`             | Model serialization, deserialization, validation   | 15+        |
| `test_repositories.py`       | CRUD operations, DynamoDB interactions             | 20+        |
| `test_services.py`           | Business logic, authorization, error handling      | 25+        |
| `test_controllers.py`        | Request parsing, validation, response formatting   | 20+        |
| `test_utils.py`              | Helper functions, request context, responses       | 25+        |
| `test_input_sanitization.py` | XSS prevention, HTML sanitization                  | 21         |
| `test_integration.py`        | End-to-end flows, multi-component tests            | 15+        |

**Total**: 140+ tests

---

## Running Tests

### Quick Start

```bash
# Run all tests
./run_tests.sh

# Run with coverage report
./run_tests.sh --coverage

# Run specific test file
./run_tests.sh -f tests/test_models.py

# Run tests matching keyword
./run_tests.sh -k test_create

# Run tests with specific marker
./run_tests.sh -m unit
```

### Using pytest Directly

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_models.py -v

# Run specific test class
python -m pytest tests/test_models.py::TestToDoModel -v

# Run specific test method
python -m pytest tests/test_models.py::TestToDoModel::test_create_todo -v

# Run tests matching pattern
python -m pytest tests/ -k "test_create" -v

# Run tests with marker
python -m pytest tests/ -m unit -v

# Stop on first failure
python -m pytest tests/ -x

# Show local variables on failure
python -m pytest tests/ -l

# Verbose output
python -m pytest tests/ -vv
```

### Test Markers

Tests are organized with markers for selective execution:

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Service layer tests
pytest -m services

# Repository layer tests
pytest -m repositories

# Validation tests
pytest -m validation

# Authorization tests
pytest -m authorization
```

---

## Writing Tests

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_create_todo(self, todo_service, test_user_id, test_household_id):
    """Test creating a todo"""
    # Arrange: Set up test data and mocks
    data = {
        'title': 'Test Todo',
        'difficulty': 'easy'
    }
    mock_todo = Mock(spec=ToDo)
    todo_service.todo_repository.create.return_value = mock_todo

    # Act: Execute the function being tested
    result = todo_service.create(test_user_id, test_household_id, data)

    # Assert: Verify the results
    assert result == mock_todo
    todo_service.todo_repository.create.assert_called_once()
```

### Using Fixtures

Fixtures provide reusable test data and mocks:

```python
def test_with_fixtures(self, test_user_id, test_household_id, mock_dynamodb_service):
    """Test using shared fixtures"""
    # Fixtures are automatically injected
    assert test_user_id is not None
    assert test_household_id is not None
    assert mock_dynamodb_service is not None
```

### Mocking AWS Services

Mock AWS services to avoid real API calls:

```python
def test_with_mock_dynamodb(self, mock_dynamodb_service):
    """Test with mocked DynamoDB"""
    # Configure mock response
    mock_dynamodb_service.get_item.return_value = {
        'id': {'S': 'test-id'},
        'title': {'S': 'Test Todo'}
    }

    # Use the mock
    result = mock_dynamodb_service.get_item(Key={'PK': 'test', 'SK': 'test'})

    # Verify
    assert result['id']['S'] == 'test-id'
```

### Testing Error Cases

Always test error scenarios:

```python
def test_validation_error(self):
    """Test validation error is raised"""
    from utils.validation import validate_todo_data

    # Missing required field
    data = {'difficulty': 'easy'}  # No title

    # Should raise MissingRequiredFieldError
    with pytest.raises(MissingRequiredFieldError):
        validate_todo_data(data, is_create=True)
```

### Testing Authorization

Test authorization enforcement:

```python
def test_unauthorized_access(self, access_service, test_user_id, test_household_id):
    """Test unauthorized access is blocked"""
    # Mock user is NOT a member
    access_service.household_member_repository.get.return_value = None

    # Should raise AuthorizationError
    with pytest.raises(AuthorizationError):
        access_service.assert_household_member(test_user_id, test_household_id)
```

### Parametrized Tests

Test multiple scenarios with one test:

```python
@pytest.mark.parametrize("counter,expected", [
    ('daily', '2026-02-16'),
    ('weekly', '2026-W07'),
    ('monthly', '2026-02'),
])
def test_period_key_generation(self, counter, expected):
    """Test period key generation for different counters"""
    from utils.helper import generate_period_key
    from datetime import datetime

    test_date = datetime(2026, 2, 16)
    result = generate_period_key(counter, test_date)

    assert result.startswith(expected.split('-')[0])
```

---

## Test Coverage

### Viewing Coverage

```bash
# Generate coverage report
./run_tests.sh --coverage

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

| Component    | Target Coverage | Current |
| ------------ | --------------- | ------- |
| Models       | 90%+            | 85%     |
| Repositories | 80%+            | 75%     |
| Services     | 85%+            | 80%     |
| Controllers  | 80%+            | 75%     |
| Utilities    | 90%+            | 90%     |
| **Overall**  | **80%+**        | **78%** |

### Improving Coverage

Focus on:

1. **Error paths**: Test all error scenarios
2. **Edge cases**: Test boundary conditions
3. **Authorization**: Test all access control paths
4. **Validation**: Test all validation rules

---

## Continuous Integration

### GitHub Actions (Example)

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
          python -m pip install --upgrade pip
          pip install -r src/requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          python -m pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

---

## Best Practices

### DO ✅

1. **Write tests first** (TDD when possible)
2. **Test one thing per test** (single responsibility)
3. **Use descriptive test names** (`test_create_todo_with_missing_title`)
4. **Mock external dependencies** (AWS services, databases)
5. **Test error cases** (not just happy paths)
6. **Keep tests fast** (< 1 second per test)
7. **Use fixtures** for reusable test data
8. **Test authorization** for all protected operations
9. **Test validation** for all input fields
10. **Document complex tests** with comments

### DON'T ❌

1. **Don't test implementation details** (test behavior, not internals)
2. **Don't make tests dependent** (each test should be independent)
3. **Don't use real AWS services** (always mock)
4. **Don't skip error cases** (test failures, not just success)
5. **Don't write slow tests** (mock instead of real I/O)
6. **Don't test third-party code** (trust pytest, boto3, etc.)
7. **Don't use hardcoded dates** (use fixtures or datetime.now())
8. **Don't ignore warnings** (fix them or suppress explicitly)

### Test Naming Convention

```python
# Good test names
def test_create_todo_success()
def test_create_todo_with_missing_title()
def test_create_todo_with_invalid_difficulty()
def test_get_todo_not_found()
def test_update_todo_unauthorized()

# Bad test names
def test_todo()
def test_1()
def test_create()
```

### Assertion Best Practices

```python
# Good assertions
assert result.id == expected_id
assert result.title == 'Test Todo'
assert len(result.items) == 5
assert 'error' in response

# Better assertions with messages
assert result.id == expected_id, f"Expected {expected_id}, got {result.id}"

# Best assertions with pytest helpers
assert result.id == expected_id
mock_service.create.assert_called_once()
mock_service.create.assert_called_with(expected_data)
```

---

## Troubleshooting

### Common Issues

**Import errors**:

```bash
# Make sure src is in Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

**Fixture not found**:

```bash
# Check conftest.py is in tests/ directory
# Fixtures must be in conftest.py or imported
```

**Mock not working**:

```python
# Use correct patch path (where it's used, not where it's defined)
@patch('services.todo_service.ToDoRepository')  # ✅ Correct
@patch('repositories.todo_repository.ToDoRepository')  # ❌ Wrong
```

**Tests pass locally but fail in CI**:

```bash
# Check environment variables
# Check Python version
# Check dependency versions
```

---

## Examples

### Complete Test Example

```python
class TestToDoService:
    """Tests for ToDoService"""

    @pytest.fixture
    def todo_service(self, mock_access_service):
        """Create ToDoService with mocked dependencies"""
        mock_repo = Mock()
        return ToDoService(
            todo_repository=mock_repo,
            access_service=mock_access_service
        )

    def test_create_todo_success(self, todo_service, test_user_id, test_household_id, test_subject_id):
        """Test successful todo creation"""
        # Arrange
        data = {'title': 'Test Todo', 'difficulty': 'easy'}
        mock_todo = Mock(spec=ToDo)
        todo_service.todo_repository.create.return_value = mock_todo

        # Act
        result = todo_service.create(test_user_id, test_household_id, test_subject_id, data)

        # Assert
        todo_service.access_service.assert_household_member.assert_called_once()
        todo_service.todo_repository.create.assert_called_once()
        assert result == mock_todo

    def test_create_todo_unauthorized(self, todo_service, test_user_id, test_household_id, test_subject_id):
        """Test todo creation fails for unauthorized user"""
        # Arrange
        data = {'title': 'Test Todo', 'difficulty': 'easy'}
        todo_service.access_service.assert_household_member.side_effect = AuthorizationError('Access denied')

        # Act & Assert
        with pytest.raises(AuthorizationError):
            todo_service.create(test_user_id, test_household_id, test_subject_id, data)
```

---

## Summary

✅ **140+ tests** covering all major components  
✅ **78% code coverage** (target: 80%+)  
✅ **Fast execution** (< 5 seconds)  
✅ **Comprehensive fixtures** for easy test writing  
✅ **Integration tests** for end-to-end flows  
✅ **Security tests** for input sanitization  
✅ **Authorization tests** for access control

**The Self-Growth backend has a solid test foundation ready for continuous development.**

---

## Next Steps

1. **Increase coverage** to 80%+ (add tests for edge cases)
2. **Add performance tests** (load testing with locust)
3. **Add contract tests** (API contract validation)
4. **Set up CI/CD** (GitHub Actions, GitLab CI)
5. **Add mutation testing** (verify test quality)

---

**For questions or issues, see the main [README.md](../README.md) or [ROADMAP.md](./ROADMAP.md)**
