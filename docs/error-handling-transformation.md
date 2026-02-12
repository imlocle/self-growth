# Error Handling Transformation: Before vs After

This document demonstrates the transformation from basic error handling to the enhanced error handling system in the todo handlers.

## Overview of Changes

### Before: Manual Error Handling

- Manual try/catch blocks in every handler
- Generic error messages
- Inconsistent HTTP status codes
- No structured logging
- Limited error context

### After: Enhanced Error Handling

- Decorator-based automatic error handling
- Specific error types with rich context
- Automatic HTTP status code mapping
- Structured logging with context
- Environment-aware stack traces

## Handler Transformations

### 1. Create Todo Handler

#### Before:

```python
from controllers.todo_controller import ToDoController
from models.errors import AuthorizationError, NotFoundError
from utils.response_util import success_response, error_response

class CreateToDoHandler:
    def __init__(self, event):
        self.controller = ToDoController(event)

    def handler(self):
        try:
            item = self.controller.create()
            return success_response(body=item.to_dict(), status_code=201)
        except AuthorizationError as e:
            return error_response(message=str(e), status_code=401)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except NotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            return error_response(message=str(e))

def lambda_handler(event, context):
    return CreateToDoHandler(event).handler()
```

#### After:

```python
import os
from typing import Dict, Any

from controllers.todo_controller import ToDoController
from utils.response_util import success_response
from utils.error_handler import handle_errors, log_error_with_context

class CreateToDoHandler:
    def __init__(self, event: Dict[str, Any]):
        self.controller = ToDoController(event)
        self.event = event

    def handler(self):
        # Extract context for logging
        user_id = self.event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub')
        path_params = self.event.get('pathParameters', {})
        household_id = path_params.get('householdId')
        subject_id = path_params.get('subjectId')

        try:
            item = self.controller.create()
            return success_response(body=item.to_dict(), status_code=201)
        except Exception as e:
            log_error_with_context(
                e,
                user_id=user_id,
                operation="create_todo_handler",
                household_id=household_id,
                subject_id=subject_id,
                request_id=self.event.get('requestContext', {}).get('requestId')
            )
            raise

@handle_errors(include_traceback=os.environ.get('ENVIRONMENT', 'prod') == 'dev')
def lambda_handler(event, context):
    return CreateToDoHandler(event).handler()
```

**Key Improvements:**

1. **Decorator Pattern**: `@handle_errors` automatically handles all exceptions
2. **Rich Logging**: Context includes user_id, household_id, subject_id, request_id
3. **Environment Awareness**: Stack traces only in development
4. **Type Hints**: Better code documentation and IDE support
5. **Simplified Logic**: No manual error-to-HTTP-status mapping

### 2. Get Todo Handler

#### Before:

```python
def handler(self):
    try:
        item = self.controller.get()
        return success_response(body=item.to_dict())
    except NotFoundError as e:
        return error_response(message=str(e), status_code=404)
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=str(e))
```

#### After:

```python
def handler(self):
    # Extract context for logging
    user_id = self.event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub')
    path_params = self.event.get('pathParameters', {})
    household_id = path_params.get('householdId')
    subject_id = path_params.get('subjectId')
    todo_id = path_params.get('todoId')

    try:
        item = self.controller.get()
        return success_response(body=item.to_dict())
    except Exception as e:
        log_error_with_context(
            e,
            user_id=user_id,
            operation="get_todo_handler",
            household_id=household_id,
            subject_id=subject_id,
            todo_id=todo_id,
            request_id=self.event.get('requestContext', {}).get('requestId')
        )
        raise
```

**Key Improvements:**

1. **Context Extraction**: Captures all relevant request context
2. **Structured Logging**: Every error includes operation context
3. **Re-raise Pattern**: Let the decorator handle the HTTP response
4. **Resource Identification**: Includes todo_id for specific resource errors

## Error Response Examples

### Before: Generic Error Response

```json
{
  "statusCode": 400,
  "body": "{\"message\": \"Invalid input\"}"
}
```

### After: Rich Error Response

```json
{
  "statusCode": 400,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{
    \"error\": \"VALIDATION_ERROR\",
    \"message\": \"Title is required\",
    \"details\": {
      \"field\": \"title\",
      \"provided_value\": \"\"
    }
  }"
}
```

## Logging Improvements

### Before: No Structured Logging

```
Error: Invalid input
```

### After: Rich Structured Logging

```json
{
  "error_type": "ValidationError",
  "error_message": "Title is required",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "title",
    "provided_value": ""
  },
  "http_status": 400,
  "context": {
    "user_id": "user123",
    "operation": "create_todo_handler",
    "household_id": "house456",
    "subject_id": "subject789",
    "request_id": "req-abc-123"
  }
}
```

## Error Flow Comparison

### Before: Manual Error Handling Flow

```
1. Exception occurs in service/controller
2. Handler catches specific exception types
3. Handler manually maps to HTTP status
4. Handler creates error response
5. Generic error message returned
6. No logging context
```

### After: Enhanced Error Handling Flow

```
1. Exception occurs in service/controller (with specific error type)
2. Service logs error with context
3. Exception bubbles up to handler
4. Handler logs additional context
5. Exception re-raised to decorator
6. Decorator automatically maps error to HTTP response
7. Rich error response with context returned
8. Structured logging throughout
```

## Benefits Demonstrated

### 1. **Consistency**

- All handlers follow the same pattern
- All errors have the same response structure
- All logging follows the same format

### 2. **Maintainability**

- Error handling logic centralized in decorator
- Changes to error format happen in one place
- Less boilerplate code in handlers

### 3. **Observability**

- Rich context in every error log
- Structured logging enables better monitoring
- Request tracing through request_id

### 4. **Developer Experience**

- Type hints improve IDE support
- Clear error messages aid debugging
- Environment-aware stack traces

### 5. **API Consumer Experience**

- Consistent error format across all endpoints
- Rich error details help with troubleshooting
- Proper HTTP status codes

### 6. **Production Readiness**

- No stack traces in production
- Structured logging for monitoring tools
- Rich context for incident response

## Migration Benefits

### Code Reduction

- **Before**: ~15 lines of error handling per handler
- **After**: ~5 lines of error handling per handler
- **Reduction**: ~67% less error handling boilerplate

### Error Context

- **Before**: Generic error messages
- **After**: Rich context with user, resource, and operation details

### Monitoring

- **Before**: Basic error messages in logs
- **After**: Structured JSON logs ready for monitoring tools

### Debugging

- **Before**: Limited context for troubleshooting
- **After**: Full request context and error details

This transformation demonstrates how the enhanced error handling system provides better developer experience, operational visibility, and API consumer experience while reducing code complexity and maintenance burden.

## Auth Handler Updates

The auth handlers (signup, login, confirm_signup) have been updated to follow the same pattern as todo handlers.

### Updated Auth Handlers

All auth handlers now:

- Extend `BaseHandler` for consistent error handling
- Use `@lambda_handler_with_errors` decorator
- Pass `request_context` to `AuthController`
- Use centralized validation in `validation.py`

### Auth Controller Changes

`AuthController` now:

- Extends `BaseController` for consistency
- Accepts `request_context` parameter
- Instantiates `AuthService` (was missing)
- Uses validation functions from `validation.py`:
  - `validate_login_data()` - Validates username/email and password
  - `validate_signup_data()` - Validates email, password, phone, names
  - `validate_confirm_signup_data()` - Validates email and confirmation code

### Auth Service Changes

`AuthService` now:

- Receives pre-validated data from Controller
- Removed duplicate validation logic
- Focuses on Cognito integration and business logic

### Example: Signup Handler

#### Before:

```python
from controllers.auth_controller import AuthController
from utils.response_util import success_response, error_response
from models.errors import AuthorizationError

class SignupHandler:
    def __init__(self, event):
        self.controller = AuthController(event)

    def handler(self):
        try:
            result = self.controller.signup()
            return success_response(body=result, status_code=200)
        except AuthorizationError as e:
            return error_response(message=str(e), status_code=400)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception:
            return error_response()

def lambda_handler(event, context):
    return SignupHandler(event).handler()
```

#### After:

```python
from typing import Any, Dict

from controllers.auth_controller import AuthController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response

class SignupHandler(BaseHandler):
    """Handler for POST /auth/signup"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = AuthController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("signup", self._signup)

    def _signup(self):
        """Register a new user"""
        result = self.controller.signup()
        return success_response(body=result, status_code=200)

@lambda_handler_with_errors("signup")
def lambda_handler(event, context):
    return SignupHandler(event).handler()
```

### Validation Functions

New validation functions in `validation.py`:

```python
def validate_login_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate login data (username/email and password)"""

def validate_signup_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate signup data (email, password, phone, names)"""

def validate_confirm_signup_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate confirmation data (email and code)"""
```

### Benefits

1. **Consistency**: Auth handlers now follow the same pattern as todo handlers
2. **Single Validation**: Validation happens once in Controller, not in Service
3. **Better Error Messages**: Uses specific error types (InvalidEmailError, MissingRequiredFieldError, etc.)
4. **Automatic Error Handling**: `@lambda_handler_with_errors` decorator handles all exceptions
5. **Structured Logging**: All errors logged with context via `handle_with_logging`
6. **Type Safety**: Type hints throughout for better IDE support

### Complete Handler List

All handlers now follow the enhanced error handling pattern:

**Todo Handlers:**

- `create_todo.py`
- `get_todo.py`
- `get_all_todo.py`
- `update_todo.py`
- `delete_todo.py`

**Auth Handlers:**

- `signup.py`
- `login.py`
- `confirm_signup.py`
