# Architecture Overview

## System Architecture

Self-Growth is a serverless application built on AWS, following a layered architecture pattern with clear separation of concerns and shared request context.

### High-Level Architecture

```
API Gateway (HTTP API + JWT Authorizer)
    ↓
Lambda Functions (Python 3.13)
    ↓
Handler Layer (HTTP handling + RequestContext)
    ↓
Controller Layer (Request parsing + Validation)
    ↓
Service Layer (Business logic + Authorization)
    ↓
Repository Layer (Data access)
    ↓
DynamoDB (Single table design)
```

### Technology Stack

- **Runtime**: Python 3.13
- **API Gateway**: HTTP API with JWT Authorizer (Cognito)
- **Authentication**: AWS Cognito User Pool
- **Database**: DynamoDB (single table design)
- **Infrastructure**: Terraform
- **Deployment**: AWS Lambda with Lambda Layers

## Architectural Layers

### 1. Handler Layer

**Purpose**: HTTP request/response handling, error management, and request context creation

**Responsibilities**:

- Parse Lambda event into RequestContext
- Share RequestContext with Controller
- Handle errors and convert to HTTP responses
- Log errors with full context
- Return standardized responses

**Key Pattern**: Uses `BaseHandler` with shared `RequestContext`

**Example**:

```python
class CreateToDoHandler(BaseHandler):
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        # Share RequestContext with Controller
        self.controller = ToDoController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("create_todo", self._create_todo)

    def _create_todo(self):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)
```

### 2. RequestContext (Shared Context)

**Purpose**: Single source of truth for all request data extraction

**Responsibilities**:

- Extract and cache JWT claims
- Parse path parameters, query parameters, body
- Create AuthUser from claims
- Provide convenience properties (user_id, household_id, etc.)
- Support error logging with full context

**Key Features**:

- Lazy loading: Data extracted only when accessed
- Caching: Each property extracted once per request
- Shared between Handler and Controller
- Eliminates duplicate extraction logic

**Example**:

```python
# In Handler
request_context = RequestContext(event)

# Access properties (lazy-loaded and cached)
user_id = request_context.user_id
household_id = request_context.household_id
body = request_context.body
claims = request_context.claims
auth_user = request_context.auth_user

# Share with Controller
controller = ToDoController(event, request_context=request_context)
```

### 3. Controller Layer

**Purpose**: Request parsing, validation, and orchestration

**Responsibilities**:

- Use shared RequestContext for all data access
- Validate input data (single validation point)
- Extract required parameters
- Call appropriate service methods
- Format responses

**Does NOT**:

- Perform authorization checks (Service layer)
- Contain business logic (Service layer)
- Access database directly (Repository layer)

**Key Pattern**: Validation happens in Controller only, not in Service

**Example**:

```python
class ToDoController(BaseController):
    def __init__(self, event, request_context=None, todo_service=None):
        super().__init__(event=event, request_context=request_context, require_auth=True)
        self.todo_service = todo_service or ToDoService()

    def create(self) -> ToDo:
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        # Validate input data in Controller (single validation point)
        validated_data = validate_todo_data(self.body, is_create=True)

        # Service receives pre-validated data
        return self.todo_service.create(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            data=validated_data
        )
```

### 4. Service Layer

**Purpose**: Business logic and authorization

**Responsibilities**:

- Enforce authorization rules
- Implement business logic
- Validate business rules
- Orchestrate multiple repository calls
- Accept pre-validated data from Controller

**Critical**:

- All authorization happens here, never in controllers
- No input validation (Controller handles that)

**Example**:

```python
class ToDoService:
    def create(self, user_id: str, household_id: str, subject_id: str, data: dict) -> ToDo:
        # Authorization (Service responsibility)
        self.access.assert_household_member(user_id, household_id)
        self.access.assert_subject_in_household(household_id, subject_id)

        # Business logic with pre-validated data
        now = utc_now_iso()
        todo = ToDo(
            id=generate_id(),
            household_id=household_id,
            subject_id=subject_id,
            date_created=now,
            date_modified=now,
            title=data["title"],
            description=data.get("description"),
            difficulty=data.get("difficulty", "easy"),
            status=data.get("status", "active"),
            date_due=data.get("date_due"),
            checklist=data.get("checklist")
        )

        self.todo_repo.create(todo)
        return todo
```

### 5. Repository Layer

**Purpose**: Data access abstraction

**Responsibilities**:

- DynamoDB operations (CRUD)
- Query construction
- Data mapping (DynamoDB ↔ Domain models)

**Does NOT**:

- Perform authorization
- Contain business logic
- Validate data

**Example**:

```python
class ToDoRepository(BaseRepository):
    def create(self, todo: ToDo) -> None:
        put_params = {
            "Item": {
                "pk": f"HOUSEHOLD#{todo.household_id}",
                "sk": f"SUBJECT#{todo.subject_id}#TODO#{todo.id}",
                **todo.to_dynamo()
            }
        }
        self.dynamodb_service.put(put_params)
```

## Authentication & Authorization

### Authentication Flow

1. User authenticates with Cognito (login)
2. Cognito returns access token and ID token
3. Client includes access token in Authorization header
4. API Gateway JWT Authorizer validates token
5. Lambda receives validated JWT claims in event
6. RequestContext extracts claims and creates AuthUser

### Authorization Pattern

Authorization is enforced in the Service layer using `AccessService`:

```python
# In every service method that accesses household data
self.access.assert_household_member(user_id, household_id)
self.access.assert_subject_in_household(household_id, subject_id)
```

This prevents path parameter spoofing attacks where a user tries to access another household's data.

## Data Flow Example

### Creating a ToDo

1. **Client Request**:

   ```
   POST /households/h123/subjects/s456/todos
   Authorization: Bearer <token>
   Body: { "title": "Buy groceries", "difficulty": "easy" }
   ```

2. **API Gateway**:
   - Validates JWT token
   - Adds claims to event context
   - Routes to create-todo Lambda

3. **Handler**:
   - Creates RequestContext from event
   - Shares RequestContext with Controller
   - Handles errors with full context logging

4. **Controller**:
   - Uses RequestContext for all data access
   - Validates input data (single validation point)
   - Extracts required parameters
   - Calls service with pre-validated data

5. **Service**:
   - Validates user is household member
   - Validates subject exists in household
   - Creates ToDo entity with pre-validated data
   - Calls repository

6. **Repository**:
   - Constructs DynamoDB item
   - Writes to DynamoDB

7. **Response**:
   ```json
   {
     "statusCode": 201,
     "body": {
       "id": "todo789",
       "title": "Buy groceries",
       "difficulty": "easy",
       ...
     }
   }
   ```

## Error Handling

### Error Hierarchy

```
BaseError (base exception)
├── ValidationError (400)
│   ├── MissingRequiredFieldError
│   ├── InvalidUsernameError
│   ├── InvalidEmailError
│   ├── InvalidPhoneError
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
    │   ├── UserNotConfirmedError
    │   ├── InvalidCredentialsError
    │   └── InvalidConfirmationCodeError
    └── DynamoDBError
        └── ConditionalCheckFailedError
```

### Error Response Format

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Title is required",
  "details": {
    "field": "title"
  }
}
```

### Error Handling Flow

1. Exception raised in any layer
2. Propagates up to handler
3. Handler catches with `@handle_errors` decorator
4. Logs error with full RequestContext
5. Returns standardized error response with appropriate HTTP status

## Design Principles

### 1. Separation of Concerns

Each layer has a single, well-defined responsibility:

- Handlers: HTTP + RequestContext creation
- RequestContext: Data extraction (single source of truth)
- Controllers: Parsing + Validation
- Services: Logic + Authorization
- Repositories: Data access

### 2. Single Validation Point

Input validation happens in Controller only:

- Controller validates and normalizes input
- Service receives pre-validated data
- No duplicate validation logic
- Clear separation of concerns

### 3. Shared RequestContext

RequestContext eliminates duplicate extraction:

- Created once in Handler
- Shared with Controller
- Lazy loading and caching
- Single source of truth for all request data

### 4. Authorization in Services

Authorization checks MUST happen in the service layer, never in controllers. This ensures:

- Consistent security enforcement
- No bypassing of authorization
- Clear audit trail

### 5. Single Table Design

All data lives in one DynamoDB table with composite keys:

- Partition Key (PK): Scopes data to household or user
- Sort Key (SK): Identifies entity type and ID
- Benefits: Atomic transactions, efficient queries, cost-effective

### 6. Explicit Ownership

Every entity has clear ownership:

```
User → Household → Subject → Entity (ToDo, Habit, etc.)
```

### 7. Pagination

All list endpoints support consistent cursor-based pagination:

- `limit`: Max items per page (1-100, optional)
- `nextToken`: Opaque base64-encoded pagination token
- `status`: Filter by entity status
- Tokens encode DynamoDB `LastEvaluatedKey` for the client
- Decoded back to `ExclusiveStartKey` on the server

### 8. Idempotency

Operations are designed to be idempotent where possible:

- Habit events use deterministic period keys
- Conditional writes prevent duplicates
- PUT operations are naturally idempotent

## Scalability Considerations

### Lambda Concurrency

- Each Lambda function scales independently
- Cold starts minimized with Lambda Layers
- Stateless design allows unlimited horizontal scaling

### DynamoDB Scaling

- On-demand billing mode
- Automatic scaling based on traffic
- Single table design reduces connection overhead

### API Gateway

- Handles millions of requests per second
- Built-in throttling and rate limiting
- Regional deployment for low latency

## Security

### Defense in Depth

1. **API Gateway**: JWT validation
2. **Service Layer**: Membership validation
3. **DynamoDB**: IAM permissions
4. **Cognito**: User authentication

### Principle of Least Privilege

- Lambda functions have minimal IAM permissions
- Users can only access their household data
- No cross-household data leakage

### Input Validation

- All inputs validated at controller layer (single point)
- Type checking with Python type hints
- Enum validation for status fields
- Specific error types for validation failures

## Monitoring & Observability

### CloudWatch Logs

- All Lambda invocations logged
- Structured logging with RequestContext
- Error logs include stack traces (dev only)
- Full request context in error logs

### Metrics

- Lambda duration and errors
- DynamoDB read/write capacity
- API Gateway request counts

### Tracing

- AWS X-Ray integration (future)
- Request ID tracking via RequestContext
- Error correlation with full context

## Future Enhancements

### Planned Improvements

1. **Caching**: Add Redis/ElastiCache for frequently accessed data
2. **Analytics**: Add time-series data for habit tracking
3. **Notifications**: SNS/SES for reminders
4. **Multi-region**: Cross-region replication for DR
5. **GraphQL**: Optional GraphQL API layer

### Non-Goals

- No ORM (direct DynamoDB access)
- No framework-heavy runtime (keep cold starts low)
- No premature abstraction (YAGNI principle)
