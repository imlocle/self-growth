# Internal Codebase Structure & Deep Dive

**For: Developers & Maintainers**

**Last Updated:** March 12, 2026

---

## Table of Contents

1. [Module Organization](#module-organization)
2. [Key File Details](#key-file-details)
3. [Data Flow Details](#data-flow-details)
4. [Extension Points](#extension-points)
5. [Module Dependencies](#module-dependencies)

---

## Module Organization

### src/aws/ — AWS Service Wrappers

**Purpose:** Abstract AWS service interactions

**Files:**

- `dynamodb_service.py` — DynamoDB operations (put, get, query, delete)
- `cognito_service.py` — Cognito user management

**When to Modify:**

- Adding new DynamoDB query patterns
- Adding Cognito features (MFA, advanced auth)
- Changing database table structure

**Key Classes:**

```python
class DynamoDBService:
    def put(table_name, item)      # Create/update
    def get(table_name, key)       # Read single
    def query(table_name, kwargs)  # Query with filters
    def delete(table_name, key)    # Delete/archive

class CognitoService:
    def signup(email, password)
    def login(email, password)
    def refresh_token(refresh_token)
    def verify_email(email, code)
```

---

### src/handlers/ — Lambda Entry Points

**Purpose:** Parse Lambda events and route to controllers

**Structure:**

```
handlers/
├── base_handler.py          # BaseHandler class
├── auth/
│   ├── signup.py           # lambda_handler(event, context)
│   ├── login.py
│   ├── refresh.py
│   └── confirm.py
├── habits/
│   ├── create.py
│   ├── get.py
│   ├── list.py
│   ├── update.py
│   ├── delete.py
│   ├── get_analytics.py
│   └── event/
│       ├── create_event.py
│       ├── list_events.py
│       └── delete_event.py
└── ... (todos, blogs, households)
```

**File Pattern - Each Handler:**

```python
def lambda_handler(event, context):
    try:
        # 1. Extract context
        user_id = get_request_context(event)["user_id"]
        body = json.loads(event.get("body", "{}"))

        # 2. Route to controller
        controller = HabitController(services)
        result = controller.create_habit(body, user_id)

        # 3. Return response
        return {
            "statusCode": 201,
            "body": json.dumps(result)
        }
    except Exception as e:
        return error_response(500, str(e))
```

**When to Add:**

- New API endpoint needed
- New resource domain (e.g., goals, projects)
- New action on existing resource

**When to Modify:**

- Changing request/response format
- Adding new parameters
- Changing authentication requirements

---

### src/controllers/ — Request Handlers

**Purpose:** Validate input, enforce business rules, format responses

**Files:**

- `base_controller.py` — Base class with utilities
- `auth_controller.py` — Authentication workflows
- `habit_controller.py` — Habit operations
- `todo_controller.py` — Todo operations
- `blog_post_controller.py` — Blog post operations
- `household_controller.py` — Household operations
- `user_profile_controller.py` — Profile operations

**Pattern - Each Controller:**

```python
class HabitController(BaseController):
    def create_habit(self, data: dict, user_id: str) -> dict:
        # 1. Validate input
        validated = validate_habit_data(data)

        # 2. Call service
        habit = self.service.create(user_id, **validated)

        # 3. Return formatted response
        return habit.to_dict()

    def list_habits(self, user_id: str, params: dict) -> list:
        # Similar pattern: validate → service → format
        pass
```

**Key Responsibilities:**

1. Input validation (type, format, length)
2. HTML sanitization (XSS prevention)
3. Service orchestration
4. Response formatting
5. Error handling and translation

**When to Modify:**

- Adding new validation rules
- Changing response structure
- Adding new business operations
- Improving error messages

---

### src/services/ — Business Logic

**Purpose:** Implement domain logic and authorization

**Files:**

- `auth_service.py` — Authentication workflows
- `habit_service.py` — Habit creation, modification, analytics
- `habit_analytics_service.py` — Streak and metrics calculation
- `todo_service.py` — Todo management
- `blog_post_service.py` — Blog operations
- `household_service.py` — Household management
- `household_member_service.py` — Member operations
- `household_subject_service.py` — Subject operations
- `user_profile_service.py` — Profile operations
- `access_service.py` — Authorization enforcement

**Service Pattern:**

```python
class HabitService:
    def __init__(self, habit_repo, habit_event_repo, access_service):
        self.habit_repo = habit_repo
        self.habit_event_repo = habit_event_repo
        self.access_service = access_service

    def create(self, user_id: str, title: str, habit_type: str) -> Habit:
        # 1. Authorize
        self.access_service.check_ownership(user_id)

        # 2. Apply business logic
        habit = Habit(
            id=uuid4(),
            user_id=user_id,
            title=title,
            type=HabitType(habit_type),
            streak=0
        )

        # 3. Persist
        return self.habit_repo.create(habit)

    def get_streaks(self, habit_id: str) -> int:
        # Complex logic: calculate streak from events
        pass
```

**Key Responsibilities:**

1. Enforce authorization (who can do what)
2. Apply business rules (validate state transitions)
3. Coordinate multiple repositories
4. Calculate metrics and analytics
5. Handle error states with meaningful messages

**When to Modify:**

- Adding business rules (e.g., "can't delete if active streak")
- Adding analytics/calculations
- Changing authorization logic
- Refactoring complex operations

---

### src/repositories/ — Data Persistence

**Purpose:** Abstract DynamoDB interactions

**Files:**

- `habit_repository.py`
- `todo_repository.py`
- `blog_post_repository.py`
- `household_repository.py`
- `household_member_repository.py`
- `household_subject_repository.py`
- `user_profile_repository.py`
- `habit_event_repository.py`

**Repository Pattern:**

```python
class HabitRepository:
    def __init__(self, dynamodb_service):
        self.dynamodb = dynamodb_service

    def create(self, habit: Habit) -> Habit:
        item = habit.to_dynamo()
        self.dynamodb.put("self_growth", item)
        return habit

    def get(self, habit_id: str) -> Optional[Habit]:
        item = self.dynamodb.get("self_growth", {"PK": f"HABIT#{habit_id}"})
        return Habit.from_dynamo(item) if item else None

    def query_by_user(self, user_id: str, limit=20) -> list:
        items = self.dynamodb.query(
            "self_growth",
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": f"USER#{user_id}"},
            Limit=limit
        )
        return [Habit.from_dynamo(item) for item in items.get("Items", [])]
```

**Key Responsibilities:**

1. CRUD operations (create, read, update, delete)
2. Query building for different patterns
3. Entity conversion (Python → DynamoDB format)
4. No business logic (just storage operations)

**When to Modify:**

- Adding new query patterns
- Changing DynamoDB schema
- Adding caching logic
- Optimizing queries

---

### src/models/ — Domain Entities

**Purpose:** Define domain objects with serialization

**Files:**

- `base_model.py` — Base class with to_dict(), from_dynamo()
- `enum.py` — Enumerations (HabitType, Status, Role, etc.)
- `errors.py` — Custom exceptions
- Individual models: `habit.py`, `todo.py`, `blog_post.py`, etc.

**Model Pattern:**

```python
@dataclass
class Habit(BaseModel):
    id: str
    user_id: str
    title: str
    type: HabitType  # Enum
    streak: int
    status: HabitStatus
    date_created: datetime
    date_modified: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type.value,
            "streak": self.streak,
            "status": self.status.value
        }

    def to_dynamo(self) -> dict:
        return {
            "PK": f"HABIT#{self.id}",
            "SK": f"USER#{self.user_id}",
            "entity": "Habit",
            "title": self.title,
            "type": self.type.value,
            "streak": self.streak,
            "status": self.status.value,
            "date_created": self.date_created.isoformat(),
            "date_modified": self.date_modified.isoformat()
        }

    @staticmethod
    def from_dynamo(item: dict) -> "Habit":
        return Habit(
            id=item["id"],
            user_id=item["user_id"],
            title=item["title"],
            type=HabitType(item["type"]),
            # ... rest of fields
        )
```

**Key Responsibilities:**

1. Define domain entity structure
2. Validate entity state
3. Serialize to/from JSON and DynamoDB
4. Provide type hints for IDE support

**When to Add:**

- New entity domain (e.g., Goals, Projects)

**When to Modify:**

- Adding new fields to entity
- Changing serialization format
- Adding validation rules

---

### src/utils/ — Utilities

**Purpose:** Shared helper functions and utilities

**Files:**

- `validation.py` — Input validation and sanitization
- `errors.py` — Error response models
- `request_context.py` — Extract context from Lambda event
- `response_utils.py` — Response formatting utilities

**Key Functions:**

```python
# validation.py
def sanitize_html(value: str) -> str
    # Remove scripts, strip tags, escape entities

def validate_habit_data(data: dict) -> dict
    # Validate and sanitize habit creation data

def validate_email(email: str) -> str
    # RFC 5321 validation, sanitization

# request_context.py
def get_request_context(event: dict) -> dict
    # Extract user_id from JWT claims

def get_query_params(event: dict) -> dict
    # Parse query parameters

# response_utils.py
def success_response(status: int, data: dict) -> dict
    # Format 2xx response

def error_response(status: int, error: str, message: str) -> dict
    # Format error response
```

**When to Modify:**

- Adding new validation rules
- Changing sanitization logic
- Adding new response formats
- Improving error messages

---

## Key File Details

### Important Files to Know

**High Priority (Core Functionality):**

1. `src/handlers/*/` — Every change touches these
2. `src/controllers/base_controller.py` — Request validation pipeline
3. `src/services/access_service.py` — Authorization enforcement
4. `src/utils/validation.py` — Input sanitization

**Medium Priority (Common Changes):**

1. `src/models/` — When adding new entities
2. `src/repositories/` — When adding new queries
3. `src/handlers/base_handler.py` — Response format changes

**Lower Priority (Rarely Changed):**

1. `src/aws/` — Only when changing AWS services
2. `tests/conftest.py` — When adding new fixtures
3. `terraform/` — Only when changing infrastructure

---

## Data Flow Details

### Complete Request Flow: Create Habit

```
1. Client Request
   POST /habits
   Authorization: Bearer <JWT>
   Content-Type: application/json
   {
     "title": "Morning Run",
     "type": "BUILD",
     "counter": "DAILY",
     "difficulty": "MEDIUM"
   }

2. API Gateway
   - JWT validation with Cognito
   - Extract claims into event context
   - Route to Lambda: habits/create

3. Lambda Handler (src/handlers/habits/create.py)
   event = {
     "body": "{\"title\": \"Morning Run\", ...}",
     "requestContext": {
       "authorizer": {
         "claims": {
           "sub": "user123",
           "email": "user@example.com"
         }
       }
     }
   }

   - Parse event.body as JSON
   - Extract claims from requestContext
   - Call controller.create_habit(body, user_id)

4. Controller (src/controllers/habit_controller.py)
   def create_habit(self, data, user_id):

   - Validate data: validate_habit_data(data)
     • Check title: 1-200 chars, not empty
     • Check type: BUILD or QUIT only
     • Check counter: DAILY, WEEKLY, MONTHLY
     • Check difficulty: EASY, MEDIUM, HARD

   - Sanitize strings: sanitize_string(title)
     • Remove HTML tags, escape entities
     • Remove null bytes
     • Trim whitespace

   - Call service: self.habit_service.create(user_id, title, ...)

5. Service (src/services/habit_service.py)
   def create(self, user_id, title, habit_type):

   - Check authorization: access_service.check_ownership(user_id)
     • Verify user is authenticated
     • Verify user owns this data

   - Create entity: Habit(id=uuid4(), user_id=user_id, ...)

   - Persist: self.habit_repo.create(habit)

6. Repository (src/repositories/habit_repository.py)
   def create(self, habit):

   - Convert to DynamoDB format: habit.to_dynamo()
     {
       "PK": "HABIT#550e8400-e29b",
       "SK": "USER#user123",
       "entity": "Habit",
       "title": "Morning Run",
       "type": "BUILD",
       "counter": "DAILY",
       "difficulty": "MEDIUM",
       "streak": 0,
       "status": "ACTIVE",
       "date_created": "2026-03-12T...",
       ...
     }

   - Call DynamoDB: dynamodb_service.put("self_growth", item)

7. DynamoDB Service (src/aws/dynamodb_service.py)
   def put(self, table_name, item):

   - Boto3 call: self.dynamodb.put_item(TableName=table_name, Item=item)
   - Wait for response
   - Return item

8. Response Flow (reverse)
   Repository ← returns Habit object
   Service ← returns Habit object
   Controller ← calls habit.to_dict() = {id, title, type, ...}
   Handler ← wraps in HTTP response:
   {
     "statusCode": 201,
     "body": "{\"id\": \"550e8400-e29b\", \"title\": \"Morning Run\", ...}",
     "headers": {"Content-Type": "application/json"}
   }

9. API Gateway
   - Returns 201 Created to client

10. Client receives:
    HTTP 201 Created
    {
      "id": "550e8400-e29b",
      "title": "Morning Run",
      "type": "BUILD",
      "counter": "DAILY",
      "difficulty": "MEDIUM",
      "streak": 0,
      "status": "ACTIVE"
    }
```

---

## Extension Points

### Adding a New Resource (e.g., "Goals")

**Step 1:** Create Model

```python
# src/models/goal.py
@dataclass
class Goal(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    target_date: datetime
    status: GoalStatus  # NOT_STARTED, IN_PROGRESS, COMPLETED, ABANDONED
    progress: int  # 0-100
    # ... timestamps, etc
```

**Step 2:** Create Repository

```python
# src/repositories/goal_repository.py
class GoalRepository:
    def create(self, goal: Goal) -> Goal: ...
    def get(self, goal_id: str) -> Goal: ...
    def query_by_user(self, user_id: str) -> list: ...
    def update(self, goal: Goal) -> Goal: ...
    def delete(self, goal_id: str): ...
```

**Step 3:** Create Service

```python
# src/services/goal_service.py
class GoalService:
    def create(self, user_id: str, title: str, ...) -> Goal:
        # Authorization, business logic, persist

    def update_progress(self, goal_id: str, progress: int) -> Goal:
        # Update and return

    # ... other operations
```

**Step 4:** Create Controller

```python
# src/controllers/goal_controller.py
class GoalController(BaseController):
    def create_goal(self, data: dict, user_id: str) -> dict:
        # Validate, call service, return dict

    def list_goals(self, user_id: str) -> list:
        # Get all goals, return list of dicts

    # ... other operations
```

**Step 5:** Create Handlers

```python
# src/handlers/goals/create.py
def lambda_handler(event, context):
    # Extract context, call controller, return response

# src/handlers/goals/list.py
# Similar pattern
```

**Step 6:** Add Tests

```python
# tests/test_models.py
def test_goal_to_dict(): ...

# tests/test_repositories.py
def test_goal_repository_create(): ...

# tests/test_services.py
def test_goal_service_create(): ...

# tests/test_controllers.py
def test_goal_controller_create(): ...

# tests/test_integration.py
def test_create_and_list_goals_workflow(): ...
```

**Step 7:** Register in Terraform

```hcl
# terraform/modules/lambda/main.tf
resource "aws_lambda_function" "goal_create" {
  filename = ...
  function_name = "goal-create"
  handler = "src/handlers/goals/create.lambda_handler"
  # ... other config
}

# And repeat for other handlers (list, get, update, delete)

# terraform/main.tf
resource "aws_apigatewayv2_route" "goal_create" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /goals"
  target    = "integrations/${aws_apigatewayv2_integration.goal_create.id}"
}
```

## Done! You now have a new resource fully integrated.

---

## Module Dependencies

### Import Map (What imports what)

```
Handlers
└── Controllers
    ├── Services
    │   ├── Repositories
    │   │   └── DynamoDB Service
    │   ├── Access Service
    │   │   └── Repositories
    │   ├── Other Services
    │   └── CognitoService
    ├── Validation Utilities
    └── Error Models

Models
└── Used by: Services, Repositories, Controllers, Handlers

Utils
└── Used by: Everyone (validation, errors, response formatting)
```

### Circular Dependency Check

**Allowed:**

- Controllers → Services → Repositories
- Services → Other Services (e.g., HabitService → AccessService)
- All → Utils, Models

**Not Allowed (Would Cause Cycles):**

- Repositories → Services (breaks abstraction)
- Handlers → Services directly (they should go through controllers)
- Models → Services (models should be passive)

---

**Last Updated:** March 12, 2026
