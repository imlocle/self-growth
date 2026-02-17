# Service and Repository Reference

## Architecture Overview

The application follows a layered architecture with clear separation of concerns:

```
Handler (RequestContext) → Controller (Validation) → Service (Authorization + Logic) → Repository → DynamoDB
```

**Key Principles:**

- Authorization lives in services, never in controllers or repositories
- Validation happens in controllers, never in services
- RequestContext is shared between Handler and Controller
- Services receive pre-validated data from controllers

## Service Layer

Services contain business logic, authorization, and orchestration. They validate user permissions before executing operations and coordinate between multiple repositories when needed.

**Important**: Services accept pre-validated data from controllers. No input validation happens in services.

### AccessService

Centralized authorization service used by all other services.

**Purpose:** Validates user permissions for household-scoped operations.

**Methods:**

#### `assert_household_member(user_id: str, household_id: str) -> None`

Validates that a user is a member of the specified household.

**Parameters:**

- `user_id`: Cognito user identifier
- `household_id`: Household identifier

**Raises:**

- `HouseholdMembershipError`: User is not a member of the household
- `NotFoundError`: Household or user not found

**Usage:** Called by all household-scoped service methods.

#### `assert_subject_in_household(household_id: str, subject_id: str) -> None`

Validates that a subject exists within the specified household.

**Parameters:**

- `household_id`: Household identifier
- `subject_id`: Subject identifier

**Raises:**

- `SubjectNotFoundError`: Subject not found in household

**Usage:** Called by all subject-scoped service methods.

### UserProfileService

Manages user profile operations.

**Dependencies:**

- `UserProfileRepository`
- `HouseholdRepository`
- `HouseholdSubjectRepository`
- `HouseholdMemberRepository`

**Methods:**

#### `create(user_id: str, data: dict) -> UserProfile`

Creates a new user profile with associated household and subject.

**Parameters:**

- `user_id`: Cognito user identifier
- `data`: Pre-validated user profile data from controller

**Business Logic:**

1. Creates household for user
2. Creates default subject
3. Creates household membership
4. Creates user profile

**Returns:** Created UserProfile object

#### `get(user_id: str) -> UserProfile`

Retrieves user profile by user ID.

#### `update(user_id: str, data: dict) -> UserProfile`

Updates existing user profile.

**Parameters:**

- `user_id`: Cognito user identifier
- `data`: Pre-validated update data from controller

### ToDoService

Manages todo operations with household/subject scoping.

**Dependencies:**

- `ToDoRepository`
- `AccessService`

**Authorization Pattern:**
All methods validate:

1. User is household member
2. Subject exists in household

**Methods:**

#### `create(user_id: str, household_id: str, subject_id: str, data: dict) -> ToDo`

Creates a new todo for a subject.

**Parameters:**

- `user_id`: User ID (for authorization)
- `household_id`: Household ID
- `subject_id`: Subject ID
- `data`: Pre-validated todo data from controller

**Authorization:**

- Validates user is household member
- Validates subject exists in household

**Business Logic:**

1. Generates unique todo ID
2. Sets creation timestamps
3. Creates ToDo entity with pre-validated data
4. Saves to repository

**Example:**

```python
def create(self, user_id: str, household_id: str, subject_id: str, data: dict) -> ToDo:
    # Authorization
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
        title=data["title"],  # Already validated by controller
        description=data.get("description"),
        difficulty=data.get("difficulty", "easy"),
        status=data.get("status", "active"),
        date_due=data.get("date_due"),
        checklist=data.get("checklist")
    )

    self.todo_repo.create(todo)
    return todo
```

#### `get(user_id: str, household_id: str, subject_id: str, todo_id: str) -> ToDo`

Retrieves a specific todo.

**Raises:**

- `NotFoundError`: If todo not found

#### `get_all(user_id: str, household_id: str, subject_id: str, sort_by: str = "date_modified", limit: int = None, next_token: dict = None, status: str = None) -> dict`

Retrieves all todos for a subject with sorting, pagination, and filtering.

**Sorting Options:**

- `date_due`: Sort by due date (nulls last)
- `date_modified`: Sort by modification date (default)

**Pagination:**

- `limit`: Max items per page (1-100)
- `next_token`: DynamoDB ExclusiveStartKey for cursor-based pagination
- `status`: Filter by status (active, completed, deleted)

**Returns:**

```python
{
    "items": [ToDo, ...],
    "lastEvaluatedKey": {...}  # For pagination
}
```

#### `update(user_id: str, household_id: str, subject_id: str, todo_id: str, data: dict) -> ToDo`

Updates an existing todo.

**Parameters:**

- `data`: Pre-validated update data from controller

**Business Logic:**

- Partial updates supported
- Updates `date_modified` timestamp
- Uses pre-validated data from controller

#### `delete(user_id: str, household_id: str, subject_id: str, todo_id: str) -> None`

Soft deletes a todo by setting status to DELETED.

### HabitService

Manages habit operations with household/subject scoping.

**Dependencies:**

- `HabitRepository`
- `AccessService`

**Methods:** Similar to ToDoService (create, get, get_all, update, delete)

**Special Behavior:**

- Soft deletion sets status to DELETED
- Supports habit types: build/quit
- Counter types: daily/weekly/monthly

### HabitEventService

Manages habit event logging with period-based constraints.

**Dependencies:**

- `HabitEventRepository`
- `HabitRepository`
- `AccessService`

### HabitAnalyticsService

Lightweight on-the-fly analytics computed from habit events.

**Dependencies:**

- `HabitEventRepository`
- `HabitRepository`
- `AccessService`

**Methods:**

#### `get_analytics(user_id: str, household_id: str, subject_id: str, habit_id: str) -> dict`

Computes analytics for a habit from all its events.

**Returns:**

```python
{
    "habit_id": "...",
    "counter": "daily",
    "total_events": 45,
    "distribution": {"done": 38, "skipped": 5, "failed": 2},
    "completion_rate": 0.8444,
    "current_streak": 7,
    "longest_streak": 14,
    "first_event_date": "2025-11-01T08:00:00Z",
    "last_event_date": "2026-02-16T07:30:00Z",
}
```

**Computation:**

- Fetches all events for the habit
- Calculates streaks based on consecutive period keys (daily/weekly/monthly)
- Current streak counts backwards from today/yesterday
- Completion rate = done / total events

**Dependencies:**

- `HabitEventRepository`
- `HabitRepository`
- `AccessService`

**Methods:**

#### `create(user_id: str, household_id: str, subject_id: str, habit_id: str, data: dict) -> HabitEvent`

Creates a habit event for a specific period.

**Parameters:**

- `data`: Pre-validated habit event data from controller

**Authorization:**

- Validates user is household member
- Validates subject exists in household
- Validates habit exists for subject

**Business Logic:**

1. Retrieves habit to determine counter type
2. Calculates period key based on current date and counter type
3. Attempts conditional write to prevent duplicates
4. Returns created event or raises ConflictError if duplicate

**Period Key Generation:**

- Daily: `YYYY-MM-DD` (e.g., "2025-01-15")
- Weekly: `YYYY-Www` (e.g., "2025-W03")
- Monthly: `YYYY-MM` (e.g., "2025-01")

**Idempotency:** Same habit + same period = same DynamoDB key

**Raises:**

- `HabitEventConflictError`: Event already exists for the period

### AuthService

Manages authentication operations via AWS Cognito.

**Dependencies:**

- `CognitoService` (AWS Cognito Client wrapper)

**Methods:**

#### `login(username: str, password: str) -> dict`

Authenticates user and returns JWT tokens.

**Returns:**

```python
{
    "access_token": "...",
    "id_token": "...",
    "refresh_token": "...",
    "expires_in": 3600
}
```

**Raises:**

- `InvalidCredentialsError`: Invalid username or password
- `UserNotConfirmedError`: User account not confirmed

#### `signup(email: str, password: str, phone_number: str, first_name: str, last_name: str) -> dict`

Registers new user in Cognito.

**Returns:**

```python
{
    "user_id": "...",
    "email": "...",
    "confirmation_required": true
}
```

**Raises:**

- `EmailConflictError`: Email already registered
- `CognitoError`: Cognito service error

#### `confirm_signup(email: str, confirmation_code: str) -> dict`

Confirms user signup with email verification code.

**Raises:**

- `InvalidConfirmationCodeError`: Invalid or expired code
- `CognitoError`: Cognito service error

#### `get_user_from_cognito(access_token: str) -> AuthUser`

Fetches full user details from Cognito using access token.

**Usage:** Called when JWT claims don't contain all needed attributes (e.g., email not in claims).

**Returns:** AuthUser object with full user details

**Raises:**

- `CognitoError`: Cognito service error

#### `refresh_token(refresh_token: str) -> dict`

Refreshes expired access tokens using a refresh token.

**Returns:**

```python
{
    "access_token": "...",
    "id_token": "...",
    "expires_in": 3600
}
```

**Raises:**

- `AuthenticationError`: Invalid or expired refresh token

## Repository Layer

Repositories handle DynamoDB operations only. They contain no business logic, authorization, or validation.

### BaseRepository

Provides common DynamoDB initialization and helper methods.

**Attributes:**

- `dynamodb_service`: Initialized DynamodbService instance

**Helper Methods:**

- `household_pk(household_id: str) -> str`: Returns `HOUSEHOLD#{household_id}`
- `subject_sk(subject_id: str) -> str`: Returns `SUBJECT#{subject_id}`

### ToDoRepository

Handles DynamoDB operations for todos.

**Key Pattern:**

- PK: `HOUSEHOLD#{household_id}`
- SK: `SUBJECT#{subject_id}#TODO#{todo_id}`

**Methods:**

#### `create(todo: ToDo) -> None`

Puts todo item in DynamoDB.

#### `get(household_id: str, subject_id: str, todo_id: str) -> dict | None`

Retrieves single todo by composite key.

**Returns:** DynamoDB item dict or None if not found

#### `get_all(household_id: str, subject_id: str, limit: int = None, next_token: dict = None, filter_expression: str = None, ...) -> dict`

Queries all todos for a subject using `begins_with` on sort key. Supports pagination and filtering.

**Query Pattern:**

```python
pk = f"HOUSEHOLD#{household_id}"
sk_prefix = f"SUBJECT#{subject_id}#TODO#"
# Query with begins_with(sk, sk_prefix)
# Optional: Limit, ExclusiveStartKey, FilterExpression
```

**Returns:**

```python
{
    "items": [dict, ...],
    "lastEvaluatedKey": {...}  # For pagination
}
```

#### `update(todo: ToDo) -> None`

Overwrites existing todo item (updates `date_modified`).

#### `delete(todo: ToDo) -> dict`

Deletes todo item from DynamoDB.

### HabitRepository

Handles DynamoDB operations for habits.

**Key Pattern:**

- PK: `HOUSEHOLD#{household_id}`
- SK: `SUBJECT#{subject_id}#HABIT#{habit_id}`

**Methods:** Similar to ToDoRepository

### HabitEventRepository

Handles DynamoDB operations for habit events.

**Key Pattern:**

- PK: `HOUSEHOLD#{household_id}`
- SK: `SUBJECT#{subject_id}#HABIT#{habit_id}#EVENT#{period_key}`

**Methods:**

#### `create(event: HabitEvent) -> None`

Creates habit event with conditional write to prevent duplicates.

**Conditional Expression:** `attribute_not_exists(pk) AND attribute_not_exists(sk)`

**Behavior:** Raises `ConditionalCheckFailedError` if event already exists for the period.

**Error Handling:**

```python
try:
    self.habit_event_repo.create(event)
except ConditionalCheckFailedError:
    raise HabitEventConflictError(habit_id, period_key)
```

#### `get_all(household_id: str, subject_id: str, habit_id: str) -> dict`

Queries all events for a specific habit.

### UserProfileRepository

Handles DynamoDB operations for user profiles.

**Key Pattern:**

- PK: `AUTHUSER#{user_id}`
- SK: `META#PROFILE`

### HouseholdRepository

Handles DynamoDB operations for households.

**Key Pattern:**

- PK: `HOUSEHOLD#{household_id}`
- SK: `META#HOUSEHOLD`

### HouseholdMemberRepository

Handles DynamoDB operations for household memberships.

**Key Pattern:**

- PK: `HOUSEHOLD#{household_id}`
- SK: `MEMBER#{user_id}`

### HouseholdSubjectRepository

Handles DynamoDB operations for household subjects.

**Key Pattern:**

- PK: `HOUSEHOLD#{household_id}`
- SK: `SUBJECT#{subject_id}`

## DynamodbService

Low-level DynamoDB operations wrapper.

**Methods:**

#### `get(request: dict) -> dict`

Executes DynamoDB GetItem operation.

#### `put(request: dict) -> dict`

Executes DynamoDB PutItem operation.

#### `update(request: dict) -> dict`

Executes DynamoDB UpdateItem operation.

#### `query(request: dict) -> dict`

Executes DynamoDB Query operation.

#### `delete(request: dict) -> dict`

Executes DynamoDB DeleteItem operation.

#### `batch_get(request: dict) -> dict`

Executes DynamoDB BatchGetItem operation.

**Response Processing:**

- Parses DynamoDB responses
- Extracts items and pagination tokens
- Handles DynamoDB-specific data types

## Dependency Injection Pattern

All services support dependency injection for testing:

```python
class ToDoService:
    def __init__(
        self,
        todo_repo: ToDoRepository | None = None,
        access_service: AccessService | None = None,
    ):
        self.todo_repo = todo_repo or ToDoRepository()
        self.access = access_service or AccessService()
```

**Benefits:**

- Easy to mock for unit testing
- Flexible initialization
- Clear dependency declarations
- Supports test doubles

## Error Handling Patterns

### Service Layer Errors

Services raise specific error types from `src/models/errors.py`:

- `ValidationError`: Input validation failed (should not happen - controller validates)
- `AuthenticationError`: User not authenticated
- `AuthorizationError`: User lacks permission
  - `HouseholdMembershipError`: User not a household member
- `NotFoundError`: Resource not found
  - `SubjectNotFoundError`: Subject not found in household
- `ConflictError`: Resource already exists
  - `HabitEventConflictError`: Event already exists for period
  - `UsernameConflictError`: Username already taken
  - `EmailConflictError`: Email already registered
- `BusinessRuleError`: Business rule violation
- `ExternalServiceError`: External service error
  - `CognitoError`: Cognito service error
  - `DynamoDBError`: DynamoDB service error

### Repository Layer Errors

- DynamoDB exceptions bubble up to service layer
- No business logic errors at repository level
- Service layer converts DynamoDB errors to domain errors

**Example:**

```python
# In Repository
try:
    self.dynamodb_service.put(params)
except ClientError as e:
    if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
        raise ConditionalCheckFailedError(...)
    raise DynamoDBError(...)
```

## Authorization Flow

Every service method follows this pattern:

```python
def create(self, user_id: str, household_id: str, subject_id: str, data: dict):
    # 1. Validate user is household member
    self.access.assert_household_member(user_id, household_id)

    # 2. Validate subject exists in household
    self.access.assert_subject_in_household(household_id, subject_id)

    # 3. Execute business logic with pre-validated data
    # No input validation needed - controller already validated
    todo = ToDo(
        id=generate_id(),
        title=data["title"],  # Already validated
        ...
    )
```

This ensures:

- Consistent authorization across all endpoints
- Prevention of path parameter spoofing
- Centralized permission logic
- Clear audit trail for access decisions
- No duplicate validation logic

## Validation Flow

Validation happens in the Controller layer only:

```python
# In Controller
class ToDoController(BaseController):
    def create(self) -> ToDo:
        # Validate input data (single validation point)
        validated_data = validate_todo_data(self.body, is_create=True)

        # Service receives pre-validated data
        return self.todo_service.create(
            user_id=self.user_id,
            household_id=self.require_household_id(),
            subject_id=self.require_subject_id(),
            data=validated_data
        )
```

**Benefits:**

- Single validation point (no duplication)
- Clear separation of concerns
- Services focus on business logic
- Easier to maintain and test

## RequestContext Integration

Services don't interact with RequestContext directly. Controllers use RequestContext to extract data and pass it to services:

```python
# In Controller
class ToDoController(BaseController):
    def __init__(self, event, request_context=None, todo_service=None):
        super().__init__(event=event, request_context=request_context, require_auth=True)
        self.todo_service = todo_service or ToDoService()

    def create(self) -> ToDo:
        # Use RequestContext properties
        user_id = self.user_id  # From request_context.auth_user
        household_id = self.require_household_id()  # From request_context
        subject_id = self.require_subject_id()  # From request_context

        # Validate and pass to service
        validated_data = validate_todo_data(self.body, is_create=True)
        return self.todo_service.create(user_id, household_id, subject_id, validated_data)
```

This maintains clean separation:

- RequestContext: Data extraction
- Controller: Validation and orchestration
- Service: Authorization and business logic
- Repository: Data access
