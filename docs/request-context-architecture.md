# RequestContext Architecture

## Overview

The `RequestContext` class provides a single source of truth for extracting and managing Lambda event data. It's shared between Handlers and Controllers to eliminate duplicate extraction logic.

## Architecture Diagram

```
Lambda Event
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RequestContext                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Extracts & Caches (Lazy Loading):                       │    │
│  │ • JWT claims (user_id, email)                           │    │
│  │ • Path parameters (household_id, subject_id, todo_id)   │    │
│  │ • Query parameters                                      │    │
│  │ • Request body (parsed, snake_case)                     │    │
│  │ • Request metadata (request_id, http_method, path)      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
    │                           │
    │ (shared reference)        │ (shared reference)
    ▼                           ▼
┌──────────────────┐    ┌──────────────────┐
│   BaseHandler    │    │  BaseController  │
│                  │    │                  │
│ Uses for:        │    │ Uses for:        │
│ • Error logging  │    │ • Auth user      │
│ • Request context│    │ • Path params    │
│                  │    │ • Body parsing   │
│                  │    │ • Query params   │
└──────────────────┘    └──────────────────┘
    │                           │
    ▼                           ▼
┌──────────────────┐    ┌──────────────────┐
│  ToDoHandler     │───▶│  ToDoController  │
│  (extends Base)  │    │  (extends Base)  │
└──────────────────┘    └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   ToDoService    │
                        │                  │
                        │ Receives:        │
                        │ • user_id        │
                        │ • household_id   │
                        │ • subject_id     │
                        │ • todo_id        │
                        │ • data           │
                        └──────────────────┘
```

## Key Benefits

### 1. Single Source of Truth

- All context extraction happens in `RequestContext`
- No duplicate extraction logic in Handler or Controller
- Consistent data across all layers

### 2. Lazy Loading & Caching

```python
@property
def claims(self) -> Dict[str, Any]:
    """JWT claims - extracted once, cached for reuse"""
    if self._claims_cache is None:
        self._claims_cache = (
            self.event.get('requestContext', {})
            .get('authorizer', {})
            .get('jwt', {})
            .get('claims', {})
        ) or {}
    return self._claims_cache
```

### 3. Shared Between Layers

```python
# Handler creates RequestContext
class CreateToDoHandler(BaseHandler):
    def __init__(self, event):
        super().__init__(event)  # Creates self.request_context

        # Share with Controller - no duplicate extraction
        self.controller = ToDoController(event, request_context=self.request_context)
```

### 4. Clean API

```python
# Convenience properties
context.user_id          # From JWT claims
context.household_id     # From path params
context.subject_id       # From path params
context.todo_id          # From path params
context.body             # Parsed JSON with snake_case keys
context.query_params     # Query string parameters

# Require methods (raise ValidationError if missing)
context.require_household_id()
context.require_subject_id()
context.require_todo_id()
context.require_auth()

# Logging integration
context.logging_context  # Dict ready for error logging
context.log_error(error, "operation_name")
```

## File Structure

```
src/
├── utils/
│   └── request_context.py    # RequestContext class
├── handlers/
│   ├── base_handler.py       # BaseHandler (uses RequestContext)
│   └── todos/
│       ├── create_todo.py    # Shares RequestContext with Controller
│       ├── get_todo.py
│       ├── get_all_todo.py
│       ├── update_todo.py
│       └── delete_todo.py
└── controllers/
    ├── base_controller.py    # BaseController (uses RequestContext)
    └── todo_controller.py    # ToDoController
```

## Usage Examples

### Handler Usage

```python
class CreateToDoHandler(BaseHandler):
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        # Share RequestContext with Controller
        self.controller = ToDoController(event, request_context=self.request_context)

    def handler(self):
        # Automatic error logging with full context
        return self.handle_with_logging("create_todo", self._create_todo)

    def _create_todo(self):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)
```

### Controller Usage

```python
class ToDoController(BaseController):
    def __init__(self, event, request_context=None, todo_service=None):
        super().__init__(event, request_context=request_context, require_auth=True)
        self.todo_service = todo_service or ToDoService()

    def create(self) -> ToDo:
        # Use convenience properties from RequestContext
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        return self.todo_service.create(
            user_id=self.user_id,  # From auth_user
            household_id=household_id,
            subject_id=subject_id,
            data=self.body,  # Parsed body from RequestContext
        )
```

### Direct RequestContext Usage

```python
from utils.request_context import RequestContext

def some_function(event):
    ctx = RequestContext(event)

    # Access properties
    print(f"User: {ctx.user_id}")
    print(f"Household: {ctx.household_id}")
    print(f"Body: {ctx.body}")

    # Require values (raises error if missing)
    household_id = ctx.require_household_id()

    # Log errors with full context
    try:
        do_something()
    except Exception as e:
        ctx.log_error(e, "some_operation")
        raise
```

## RequestContext Properties

| Property          | Type       | Source   | Description               |
| ----------------- | ---------- | -------- | ------------------------- |
| `claims`          | `Dict`     | JWT      | Raw JWT claims            |
| `auth_user`       | `AuthUser` | JWT      | Authenticated user object |
| `user_id`         | `str`      | JWT      | User ID from claims       |
| `email`           | `str`      | JWT      | Email from claims         |
| `path_params`     | `Dict`     | Event    | Raw path parameters       |
| `household_id`    | `str`      | Path     | Household ID              |
| `subject_id`      | `str`      | Path     | Subject ID                |
| `todo_id`         | `str`      | Path     | Todo ID                   |
| `habit_id`        | `str`      | Path     | Habit ID                  |
| `query_params`    | `Dict`     | Event    | Query string parameters   |
| `body`            | `Dict`     | Event    | Parsed body (snake_case)  |
| `raw_body`        | `str`      | Event    | Raw body string           |
| `request_id`      | `str`      | Event    | AWS request ID            |
| `http_method`     | `str`      | Event    | HTTP method               |
| `path`            | `str`      | Event    | Request path              |
| `logging_context` | `Dict`     | Computed | Context for logging       |

## RequestContext Methods

| Method                          | Returns    | Description                |
| ------------------------------- | ---------- | -------------------------- |
| `require_auth()`                | `AuthUser` | Require authenticated user |
| `require_household_id()`        | `str`      | Require household ID       |
| `require_subject_id()`          | `str`      | Require subject ID         |
| `require_todo_id()`             | `str`      | Require todo ID            |
| `require_habit_id()`            | `str`      | Require habit ID           |
| `get_path_param(key, required)` | `str`      | Get path parameter         |
| `get_query_param(key, default)` | `str`      | Get query parameter        |
| `get_body_field(key, default)`  | `Any`      | Get body field             |
| `log_error(error, operation)`   | `None`     | Log error with context     |

## Migration from Old Pattern

### Before (Duplicate Extraction)

```python
# BaseHandler extracted context
class BaseHandler:
    def _extract_context(self):
        claims = self.event.get('requestContext', {}).get('authorizer', {})...
        path_params = self.event.get('pathParameters', {})
        # ... duplicate logic

# BaseController also extracted context
class BaseController:
    def _get_household_id(self):
        path = self.event.get("pathParameters") or {}
        return path.get("householdId")  # Same extraction!
```

### After (Shared RequestContext)

```python
# RequestContext extracts once
class RequestContext:
    @property
    def household_id(self):
        return self.path_params.get('householdId')

# Handler and Controller share the same instance
class CreateToDoHandler(BaseHandler):
    def __init__(self, event):
        super().__init__(event)  # Creates self.request_context
        self.controller = ToDoController(event, request_context=self.request_context)
```

## Testing

### Unit Testing RequestContext

```python
def test_request_context_extracts_user_id():
    event = {
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {'sub': 'user123', 'email': 'test@example.com'}
                }
            }
        }
    }

    ctx = RequestContext(event)

    assert ctx.user_id == 'user123'
    assert ctx.email == 'test@example.com'

def test_request_context_extracts_path_params():
    event = {
        'pathParameters': {
            'householdId': 'house123',
            'subjectId': 'subject456',
            'todoId': 'todo789'
        }
    }

    ctx = RequestContext(event)

    assert ctx.household_id == 'house123'
    assert ctx.subject_id == 'subject456'
    assert ctx.todo_id == 'todo789'

def test_request_context_parses_body():
    event = {
        'body': '{"title": "Test", "dateDue": "2025-01-15"}'
    }

    ctx = RequestContext(event)

    assert ctx.body == {'title': 'Test', 'date_due': '2025-01-15'}
```

### Testing with Shared Context

```python
def test_handler_shares_context_with_controller():
    event = create_mock_event()

    handler = CreateToDoHandler(event)

    # Verify same RequestContext instance is shared
    assert handler.request_context is handler.controller.request_context
```

## Performance Considerations

1. **Lazy Loading**: Properties are only computed when accessed
2. **Caching**: Each property is computed once per request
3. **Memory**: Single RequestContext instance shared across layers
4. **No Duplicate Work**: Extraction logic runs once, not twice

## Future Enhancements

1. **Add more resource IDs** as needed (e.g., `blog_id`, `event_id`)
2. **Add validation methods** for specific formats
3. **Add request tracing** integration (X-Ray)
4. **Add metrics collection** hooks
