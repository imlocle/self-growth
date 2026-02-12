# Context Extraction Optimization: Solutions & Analysis

## Problem Statement

The original todo handlers had repetitive context extraction code in every handler:

```python
# REPEATED IN EVERY HANDLER - 8-10 lines each time
user_id = self.event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub')
path_params = self.event.get('pathParameters', {})
household_id = path_params.get('householdId')
subject_id = path_params.get('subjectId')
todo_id = path_params.get('todoId')
request_id = self.event.get('requestContext', {}).get('requestId')
```

This led to:

- **Code duplication** across all handlers
- **Maintenance burden** when context extraction logic changes
- **Inconsistency** in what context is extracted
- **Error-prone** manual extraction in each handler

## Solution Approaches

### 1. Base Handler Class ⭐ **RECOMMENDED**

**Implementation:**

```python
class BaseHandler:
    def __init__(self, event: Dict[str, Any]):
        self.event = event
        self._context_cache = None

    @property
    def context(self) -> Dict[str, Any]:
        if self._context_cache is None:
            self._context_cache = self._extract_context()
        return self._context_cache

    def handle_with_logging(self, operation: str, handler_func):
        try:
            return handler_func()
        except Exception as e:
            self.log_error(e, operation)
            raise

# Usage in handlers:
class CreateToDoHandler(BaseHandler):
    def handler(self):
        return self.handle_with_logging("create_todo", self._create_todo)

    def _create_todo(self):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)
```

**Benefits:**

- ✅ **Maximum reusability** - works for all handler types
- ✅ **Lazy loading** - context extracted only when needed
- ✅ **Caching** - context extracted once per request
- ✅ **Extensible** - easy to add new common functionality
- ✅ **Type safe** - full IDE support and type hints
- ✅ **Consistent** - all handlers follow same pattern

**Code Reduction:**

- **Before**: ~20 lines per handler
- **After**: ~5 lines per handler
- **Reduction**: 75% less boilerplate code

### 2. Context Manager Approach

**Implementation:**

```python
class RequestContext:
    def __init__(self, event: Dict[str, Any]):
        self.event = event

    @contextmanager
    def error_logging(self, operation: str):
        try:
            yield
        except Exception as e:
            context = self._extract_context()
            log_error_with_context(e, operation=operation, **context)
            raise

# Usage:
def handler(self):
    with self.request_context.error_logging("create_todo"):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)
```

**Benefits:**

- ✅ **Pythonic** - uses context manager protocol
- ✅ **Clear scope** - error handling scope is explicit
- ✅ **Easy migration** - minimal changes to existing code
- ✅ **Functional friendly** - works well with functional programming

**Drawbacks:**

- ❌ **Less reusable** - needs to be instantiated in each handler
- ❌ **Requires with statement** - must remember to use it

### 3. Decorator Approach

**Implementation:**

```python
def with_context_logging(operation: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                context = extract_context_from_event(self.event)
                log_error_with_context(e, operation=operation, **context)
                raise
        return wrapper
    return decorator

# Usage:
@with_context_logging("create_todo")
def handler(self):
    item = self.controller.create()
    return success_response(body=item.to_dict(), status_code=201)
```

**Benefits:**

- ✅ **Minimal changes** - just add decorator
- ✅ **Very clean** - handler methods are pure business logic
- ✅ **Composable** - can combine with other decorators

**Drawbacks:**

- ❌ **Less explicit** - magic behavior hidden in decorator
- ❌ **Harder to customize** - less flexible per handler

### 4. Functional Approach

**Implementation:**

```python
def create_todo_handler(event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        controller = ToDoController(event)
        item = controller.create()
        return success_response(body=item.to_dict(), status_code=201)
    except Exception as e:
        context = extract_context(event)
        log_error_with_context(e, operation="create_todo", **context)
        raise
```

**Benefits:**

- ✅ **Simple** - no classes or complex patterns
- ✅ **Explicit** - everything is visible
- ✅ **Functional** - pure functions

**Drawbacks:**

- ❌ **Still repetitive** - context extraction in each function
- ❌ **Less reusable** - utility functions need to be called manually

## Comparison Matrix

| Approach            | Code Reduction | Reusability | Maintainability | Learning Curve | Migration Effort |
| ------------------- | -------------- | ----------- | --------------- | -------------- | ---------------- |
| **Base Handler**    | 75%            | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐      | ⭐⭐⭐         | ⭐⭐             |
| **Context Manager** | 80%            | ⭐⭐⭐      | ⭐⭐⭐⭐        | ⭐⭐⭐⭐       | ⭐⭐⭐⭐         |
| **Decorator**       | 80%            | ⭐⭐⭐      | ⭐⭐⭐          | ⭐⭐           | ⭐⭐⭐⭐⭐       |
| **Functional**      | 50%            | ⭐⭐        | ⭐⭐            | ⭐⭐⭐⭐⭐     | ⭐⭐⭐⭐⭐       |

## Implementation Results

### Before Optimization:

```python
# create_todo.py - 35 lines
class CreateToDoHandler:
    def __init__(self, event):
        self.controller = ToDoController(event)
        self.event = event

    def handler(self):
        # 8 lines of context extraction
        user_id = self.event.get('requestContext', {})...
        path_params = self.event.get('pathParameters', {})
        household_id = path_params.get('householdId')
        subject_id = path_params.get('subjectId')
        # ... more extraction

        try:
            item = self.controller.create()
            return success_response(body=item.to_dict(), status_code=201)
        except Exception as e:
            # 8 lines of error logging
            log_error_with_context(e, user_id=user_id, ...)
            raise
```

### After Optimization (Base Handler):

```python
# create_todo.py - 15 lines
class CreateToDoHandler(BaseHandler):
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = ToDoController(event)

    def handler(self):
        return self.handle_with_logging("create_todo", self._create_todo)

    def _create_todo(self):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)
```

**Results:**

- **57% reduction** in handler file size
- **100% elimination** of repetitive context extraction
- **Consistent context** across all handlers
- **Better error logging** with rich context
- **Type safety** with full IDE support

## Context Extraction Features

The optimized context extraction provides:

```python
{
    'user_id': 'user123',
    'email': 'user@example.com',
    'request_id': 'req-abc-123',
    'http_method': 'POST',
    'path': '/households/house123/subjects/subject456/todos',
    'household_id': 'house123',      # Automatically extracted
    'subject_id': 'subject456',      # Automatically extracted
    'todo_id': 'todo789',           # Automatically extracted
    'habit_id': 'habit101',         # Automatically extracted
    'query_params': {'sortBy': 'date_due'},  # If present
    'request_body_length': 156      # For POST/PUT requests
}
```

**Automatic Features:**

- **Lazy loading** - context extracted only when needed
- **Caching** - extracted once per request
- **camelCase to snake_case** conversion for consistency
- **Null filtering** - removes None values automatically
- **Extensible** - easy to add new context fields

## Migration Strategy

### Phase 1: Create Base Infrastructure

1. ✅ Create `BaseHandler` class
2. ✅ Create `lambda_handler_with_errors` decorator
3. ✅ Add context extraction logic

### Phase 2: Migrate Handlers

1. ✅ Update todo handlers to use `BaseHandler`
2. Update habit handlers (next step)
3. Update auth handlers (next step)
4. Update other handlers as needed

### Phase 3: Cleanup

1. Remove old error handling utilities (if unused)
2. Update documentation
3. Add tests for base handler functionality

## Recommendation: Base Handler Class

**Why Base Handler Class is the best choice:**

1. **Scalability** - Works for all current and future handler types
2. **Maintainability** - Changes to context extraction happen in one place
3. **Consistency** - All handlers follow the same pattern
4. **Extensibility** - Easy to add new common functionality (caching, metrics, etc.)
5. **Type Safety** - Full IDE support and type checking
6. **Team Adoption** - Clear, understandable pattern for all developers

**Next Steps:**

1. Apply the same pattern to habit handlers
2. Apply to auth handlers
3. Consider adding additional base handler features:
   - Request/response logging
   - Performance metrics
   - Caching utilities
   - Input validation helpers

The base handler approach provides the foundation for a scalable, maintainable handler architecture that will serve the application well as it grows.
