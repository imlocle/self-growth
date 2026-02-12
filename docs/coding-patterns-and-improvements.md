# Coding Patterns and Best Practices

## Current Implementation Patterns

### 1. Shared RequestContext Pattern

**Pattern**: Single source of truth for request data extraction

**Implementation**:

```python
# In Handler
class CreateToDoHandler(BaseHandler):
    def __init__(self, event):
        super().__init__(event)
        # RequestContext created in BaseHandler
        # Share with Controller
        self.controller = ToDoController(event, request_context=self.request_context)
```

**Benefits**:

- No duplicate extraction logic
- Lazy loading and caching
- Consistent data access across layers
- Easier testing and mocking

**Files**:

- `src/utils/request_context.py` - RequestContext implementation
- `src/handlers/base_handler.py` - Handler base class
- `src/controllers/base_controller.py` - Controller base class

### 2. Single Validation Point

**Pattern**: Validate input data in Controller only, not in Service

**Implementation**:

```python
# In Controller
class ToDoController(BaseController):
    def create(self) -> ToDo:
        # Validate input data (single validation point)
        validated_data = validate_todo_data(self.body, is_create=True)

        # Service receives pre-validated data
        return self.todo_service.create(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            data=validated_data
        )

# In Service
class ToDoService:
    def create(self, user_id: str, household_id: str, subject_id: str, data: dict) -> ToDo:
        # No validation - data is pre-validated
        # Focus on authorization and business logic
        self.access.assert_household_member(user_id, household_id)
        self.access.assert_subject_in_household(household_id, subject_id)

        # Use validated data directly
        todo = ToDo(
            id=generate_id(),
            title=data["title"],
            description=data.get("description"),
            ...
        )
```

**Benefits**:

- No duplicate validation logic
- Clear separation of concerns
- Easier to maintain and test
- Single place to update validation rules

**Files**:

- `src/utils/validation.py` - Validation functions
- `src/controllers/todo_controller.py` - Example implementation

### 3. Enhanced Error Handling

**Pattern**: Specific error types with rich context

**Implementation**:

```python
# Raise specific errors
raise ValidationError(
    message="Title is required",
    field="title"
)

raise NotFoundError(
    message="Todo not found",
    resource_type="todo",
    resource_id=todo_id
)

raise HouseholdMembershipError(
    user_id=user_id,
    household_id=household_id
)
```

**Error Hierarchy**:

```
BaseError
├── ValidationError (400)
│   ├── MissingRequiredFieldError
│   ├── InvalidUsernameError
│   ├── InvalidEmailError
│   └── InvalidEnumError
├── AuthenticationError (401)
├── AuthorizationError (403)
│   └── HouseholdMembershipError
├── NotFoundError (404)
│   └── SubjectNotFoundError
├── ConflictError (409)
│   ├── HabitEventConflictError
│   ├── UsernameConflictError
│   └── EmailConflictError
├── BusinessRuleError (422)
├── RateLimitError (429)
└── ExternalServiceError (502)
    ├── CognitoError
    └── DynamoDBError
```

**Benefits**:

- Automatic HTTP status code mapping
- Rich error context for debugging
- Consistent error responses
- Environment-aware stack traces

**Files**:

- `src/models/errors.py` - Error hierarchy
- `src/utils/error_handler.py` - Error handling utilities

### 4. Authorization in Services

**Pattern**: All authorization checks in Service layer

**Implementation**:

```python
class ToDoService:
    def create(self, user_id: str, household_id: str, subject_id: str, data: dict) -> ToDo:
        # Authorization checks (Service responsibility)
        self.access.assert_household_member(user_id, household_id)
        self.access.assert_subject_in_household(household_id, subject_id)

        # Business logic
        todo = ToDo(...)
        self.todo_repo.create(todo)
        return todo
```

**Benefits**:

- Consistent security enforcement
- No bypassing of authorization
- Clear audit trail
- Prevents path parameter spoofing

**Files**:

- `src/services/access_service.py` - Authorization logic
- All service files use AccessService

### 5. Lazy Loading and Caching

**Pattern**: Extract data only when needed, cache for reuse

**Implementation**:

```python
class RequestContext:
    def __init__(self, event):
        self.event = event
        self._claims_cache = None
        self._body_cache = None

    @property
    def claims(self):
        if self._claims_cache is None:
            self._claims_cache = self._extract_claims()
        return self._claims_cache

    @property
    def body(self):
        if self._body_cache is None:
            self._body_cache = self._parse_body()
        return self._body_cache
```

**Benefits**:

- Performance optimization
- Avoid redundant parsing
- Memory efficient
- Consistent data access

### 6. Dependency Injection

**Pattern**: Inject dependencies for testability

**Implementation**:

```python
class ToDoController(BaseController):
    def __init__(self, event, request_context=None, todo_service=None):
        super().__init__(event=event, request_context=request_context)
        self.todo_service = todo_service or ToDoService()

class ToDoService:
    def __init__(self, todo_repo=None, access_service=None):
        self.todo_repo = todo_repo or ToDoRepository()
        self.access = access_service or AccessService()
```

**Benefits**:

- Easy to mock for testing
- Flexible configuration
- Loose coupling
- Better testability

## Best Practices

### Handler Layer

**Do**:

- Create RequestContext from event
- Share RequestContext with Controller
- Use `@handle_errors` decorator
- Log errors with full context
- Return standardized responses

**Don't**:

- Parse event data directly (use RequestContext)
- Contain business logic
- Perform authorization checks
- Access database directly

### Controller Layer

**Do**:

- Use shared RequestContext for all data access
- Validate input data (single validation point)
- Extract required parameters
- Call service methods with pre-validated data
- Format responses

**Don't**:

- Perform authorization checks (Service layer)
- Contain business logic (Service layer)
- Access database directly (Repository layer)
- Duplicate validation logic

### Service Layer

**Do**:

- Enforce authorization rules first
- Accept pre-validated data from Controller
- Implement business logic
- Orchestrate repository calls
- Log errors with context

**Don't**:

- Validate input data (Controller handles that)
- Parse Lambda events (RequestContext handles that)
- Access DynamoDB directly (Repository handles that)

### Repository Layer

**Do**:

- Perform DynamoDB operations only
- Construct queries efficiently
- Map between DynamoDB and domain models
- Handle DynamoDB-specific errors

**Don't**:

- Perform authorization
- Contain business logic
- Validate input data

## Code Organization

### File Structure

```
src/
├── handlers/           # Lambda entry points
│   ├── base_handler.py
│   └── todos/
│       ├── create_todo.py
│       ├── get_todo.py
│       └── ...
├── controllers/        # Request parsing + validation
│   ├── base_controller.py
│   └── todo_controller.py
├── services/          # Business logic + authorization
│   ├── access_service.py
│   └── todo_service.py
├── repositories/      # Data access
│   ├── base_repository.py
│   └── todo_repository.py
├── models/           # Domain models + errors
│   ├── todo.py
│   └── errors.py
└── utils/            # Shared utilities
    ├── request_context.py
    ├── validation.py
    ├── error_handler.py
    └── helper.py
```

### Naming Conventions

- **Handlers**: `{Action}{Entity}Handler` (e.g., `CreateToDoHandler`)
- **Controllers**: `{Entity}Controller` (e.g., `ToDoController`)
- **Services**: `{Entity}Service` (e.g., `ToDoService`)
- **Repositories**: `{Entity}Repository` (e.g., `ToDoRepository`)
- **Models**: `{Entity}` (e.g., `ToDo`, `Habit`)
- **Errors**: `{Type}Error` (e.g., `ValidationError`, `NotFoundError`)

### Method Naming

- **CRUD Operations**: `create`, `get`, `get_all`, `update`, `delete`
- **Validation**: `validate_{entity}_data`
- **Authorization**: `assert_{condition}` (e.g., `assert_household_member`)
- **Helpers**: Descriptive verbs (e.g., `extract_claims`, `parse_body`)

## Testing Patterns

### Unit Testing

```python
def test_create_todo():
    # Mock dependencies
    mock_service = Mock()
    mock_context = Mock()

    # Create controller with mocks
    controller = ToDoController(
        event={},
        request_context=mock_context,
        todo_service=mock_service
    )

    # Test behavior
    controller.create()
    mock_service.create.assert_called_once()
```

### Integration Testing

```python
def test_create_todo_integration():
    # Use real RequestContext
    event = {
        "body": json.dumps({"title": "Test"}),
        "pathParameters": {"householdId": "h123", "subjectId": "s456"}
    }

    request_context = RequestContext(event)
    controller = ToDoController(event, request_context=request_context)

    # Test with real dependencies
    result = controller.create()
    assert result.title == "Test"
```

## Performance Optimizations

### 1. Lambda Layer

- Shared dependencies in Lambda Layer
- Reduces deployment package size
- Faster cold starts
- Shared across all functions

### 2. Lazy Loading

- RequestContext uses lazy loading
- Data extracted only when accessed
- Cached for subsequent access
- Reduces unnecessary parsing

### 3. Single Table Design

- All data in one DynamoDB table
- Efficient queries with composite keys
- Reduced connection overhead
- Cost-effective

### 4. Minimal Dependencies

- Only essential packages
- No heavy frameworks
- Fast cold starts
- Low memory footprint

## Security Best Practices

### 1. Input Validation

- Validate all inputs at Controller layer
- Use specific validation functions
- Reject invalid data early
- Provide clear error messages

### 2. Authorization

- Always check authorization in Service layer
- Validate household membership
- Validate subject existence
- Never trust path parameters

### 3. Error Handling

- Don't expose sensitive information
- Use generic error messages in production
- Include stack traces only in dev
- Log errors with context for debugging

### 4. Data Access

- Use parameterized queries
- Validate all identifiers
- Implement least privilege
- Audit data access

## Common Pitfalls to Avoid

### 1. Duplicate Extraction

**Bad**:

```python
# In Handler
user_id = event.get("requestContext", {}).get("authorizer", {}).get("jwt", {}).get("claims", {}).get("sub")

# In Controller
user_id = event.get("requestContext", {}).get("authorizer", {}).get("jwt", {}).get("claims", {}).get("sub")
```

**Good**:

```python
# Use shared RequestContext
request_context = RequestContext(event)
user_id = request_context.user_id
```

### 2. Duplicate Validation

**Bad**:

```python
# In Controller
validate_todo_data(data)

# In Service
validate_todo_data(data)  # Duplicate!
```

**Good**:

```python
# In Controller only
validated_data = validate_todo_data(data)

# In Service - use pre-validated data
def create(self, data: dict):
    # No validation needed
```

### 3. Authorization in Controller

**Bad**:

```python
# In Controller
if not self.is_household_member():
    raise AuthorizationError()
```

**Good**:

```python
# In Service
self.access.assert_household_member(user_id, household_id)
```

### 4. Business Logic in Repository

**Bad**:

```python
# In Repository
def create(self, todo):
    if todo.status == "deleted":
        raise ValidationError()  # Business logic!
```

**Good**:

```python
# In Service
if todo.status == "deleted":
    raise ValidationError()

# In Repository - just save
def create(self, todo):
    self.dynamodb_service.put(...)
```

## Migration Guide

### From Old Pattern to New Pattern

**Old Pattern** (Duplicate extraction):

```python
# Handler
user_id = extract_user_id(event)
household_id = extract_household_id(event)

# Controller
user_id = extract_user_id(event)
household_id = extract_household_id(event)
```

**New Pattern** (Shared RequestContext):

```python
# Handler
request_context = RequestContext(event)
controller = ToDoController(event, request_context=request_context)

# Controller
user_id = self.request_context.user_id
household_id = self.request_context.household_id
```

**Old Pattern** (Validation in Service):

```python
# Service
def create(self, data):
    validate_todo_data(data)  # Validation in service
    todo = ToDo(...)
```

**New Pattern** (Validation in Controller):

```python
# Controller
validated_data = validate_todo_data(self.body, is_create=True)
self.todo_service.create(data=validated_data)

# Service
def create(self, data):
    # No validation - data is pre-validated
    todo = ToDo(...)
```

## Summary

The current implementation follows these key patterns:

1. **Shared RequestContext**: Single source of truth for request data
2. **Single Validation Point**: Validate in Controller only
3. **Enhanced Error Handling**: Specific error types with rich context
4. **Authorization in Services**: All authorization checks in Service layer
5. **Lazy Loading**: Extract data only when needed, cache for reuse
6. **Dependency Injection**: Inject dependencies for testability

These patterns result in:

- Less code duplication
- Clearer separation of concerns
- Easier testing and maintenance
- Better performance
- Consistent security enforcement
