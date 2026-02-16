# SOURCE OF TRUTH — Self-Growth Backend

This document is the canonical reference for the **current state** of the Self-Growth backend.
If something conflicts with this file, this file wins.

---

## 1. Purpose

Self-Growth is a **personal development platform** that supports:

- **ToDos**: Task management with checklists, due dates, and difficulty levels
- **Habits**: Build or quit habits with daily/weekly/monthly tracking
- **Habit Events**: Deterministic event logging per time period
- **Blog Posts**: Personal notes and reflections with visibility controls
- **Multi-user households**: Shared accounts with membership management
- **Multiple tracked subjects**: Self, children, dependents, elders
- **Secure, multi-tenant access control**: Household-scoped data isolation

The backend is built to support **shared devices, caregiving use cases, and long-term analytics**.

---

## 2. Architecture (Authoritative)

### High-level Pattern

```
API Gateway (HTTP API, JWT Authorizer)
    ↓
Lambda Handler (RequestContext creation)
    ↓
Controller (Validation + Parsing)
    ↓
Service (Authorization + Business Logic)
    ↓
Repository (Data Access)
    ↓
DynamoDB (Single Table Design)
```

### Layer Responsibilities

#### Handler Layer

- HTTP request/response handling
- RequestContext creation and sharing
- Error logging with full context
- Standardized response formatting

#### RequestContext (Shared Context)

- Single source of truth for request data
- Lazy-loaded and cached properties
- JWT claims extraction
- Path/query/body parameter parsing
- Convenience methods for required fields

#### Controller Layer

- Request parsing and validation (SINGLE VALIDATION POINT)
- Parameter extraction via RequestContext
- Input normalization
- Service orchestration
- NO authorization logic
- NO business logic

#### Service Layer

- Authorization enforcement (ALWAYS)
- Business rule validation
- Multi-repository orchestration
- Receives pre-validated data from controllers
- NO input validation (controller handles that)

#### Repository Layer

- DynamoDB CRUD operations
- Query construction
- Data mapping (DynamoDB ↔ Domain models)
- NO authorization
- NO business logic

---

## 3. Authentication & Authorization

### Authentication

- **AWS Cognito User Pool** for user management
- **Access token** used in API Gateway JWT authorizer
- **`sub` claim** is the canonical `user_id`
- JWT claims extracted via RequestContext
- Email may not be in access token (use ID token for profile data)

### Authorization (Critical)

Authorization is enforced in **Service layer**, never in controllers or repositories.

Every scoped request validates:

1. **User is a member of the household** (`AccessService.assert_household_member`)
2. **Subject exists within the household** (`AccessService.assert_subject_in_household`)

This prevents path-parameter spoofing attacks where users try to access other households' data.

**Example:**

```python
# In every service method
self.access.assert_household_member(user_id, household_id)
self.access.assert_subject_in_household(household_id, subject_id)
```

---

## 4. DynamoDB Single Table Design

### Table Name

`SELF_GROWTH_TABLE` (environment variable)

### Partition Key (PK) Patterns

| Entity Type        | PK Pattern                 |
| ------------------ | -------------------------- |
| UserProfile        | `AUTHUSER#{user_id}`       |
| Household          | `HOUSEHOLD#{household_id}` |
| All household data | `HOUSEHOLD#{household_id}` |

### Sort Key (SK) Patterns

| Entity           | SK Pattern                                                 |
| ---------------- | ---------------------------------------------------------- |
| UserProfile      | `META#PROFILE`                                             |
| Household        | `META#HOUSEHOLD`                                           |
| HouseholdMember  | `MEMBER#{user_id}`                                         |
| Subject          | `SUBJECT#{subject_id}`                                     |
| HouseholdSubject | `SUBJECT#{subject_id}`                                     |
| ToDo             | `SUBJECT#{subject_id}#TODO#{todo_id}`                      |
| Habit            | `SUBJECT#{subject_id}#HABIT#{habit_id}`                    |
| HabitEvent       | `SUBJECT#{subject_id}#HABIT#{habit_id}#EVENT#{period_key}` |
| BlogPost         | `SUBJECT#{subject_id}#BLOG#{blog_id}`                      |

### Key Design Guarantees

- **One Habit Event per period**: Deterministic SKs prevent duplicates
- **Household-scoped queries**: All data partitioned by household
- **Hierarchical access**: SK structure enables begins_with queries
- **Idempotent writes**: Same action = same key

### Query Patterns

```python
# Get all habits for a subject
KeyConditionExpression: pk = HOUSEHOLD#{id} AND begins_with(sk, SUBJECT#{id}#HABIT#)

# Get all todos for a subject
KeyConditionExpression: pk = HOUSEHOLD#{id} AND begins_with(sk, SUBJECT#{id}#TODO#)

# Get specific habit event
Key: pk = HOUSEHOLD#{id}, sk = SUBJECT#{id}#HABIT#{id}#EVENT#{period_key}
```

---

## 5. Core Models (Authoritative)

### User

- Cognito identity (sub claim)
- Can be member of multiple households
- Managed by AWS Cognito

### UserProfile

- Application-level identity
- Fields: `user_id`, `username`, `email`, `first_name`, `last_name`, `phone_number`
- Separate from Cognito (supports future multi-profile)
- PK: `AUTHUSER#{user_id}`, SK: `META#PROFILE`

### Household

- Shared account/family/care group
- Fields: `id`, `name`, `owner_user_id`, `date_created`, `date_modified`
- PK: `HOUSEHOLD#{household_id}`, SK: `META#HOUSEHOLD`

### HouseholdMember

- Junction entity: User ↔ Household
- Fields: `household_id`, `user_id`, `role`, `date_joined`
- PK: `HOUSEHOLD#{household_id}`, SK: `MEMBER#{user_id}`

### Subject

- Individual being tracked (self, child, elder, dependent)
- Fields: `id`, `name`, `date_of_birth`, `relationship`, `date_created`, `date_modified`

### HouseholdSubject

- Junction entity: Subject ↔ Household
- PK: `HOUSEHOLD#{household_id}`, SK: `SUBJECT#{subject_id}`

### ToDo

- Task scoped to a subject
- Fields: `id`, `household_id`, `subject_id`, `title`, `description`, `difficulty`, `status`, `date_due`, `checklist`, `date_created`, `date_modified`
- Status: `active`, `completed`, `deleted`
- Difficulty: `trivial`, `easy`, `medium`, `hard`
- PK: `HOUSEHOLD#{household_id}`, SK: `SUBJECT#{subject_id}#TODO#{todo_id}`

### Habit

- Definition of a habit to build or quit
- Fields: `id`, `household_id`, `subject_id`, `title`, `description`, `counter`, `difficulty`, `type`, `status`, `date_created`, `date_modified`
- Counter: `daily`, `weekly`, `monthly`
- Type: `build`, `quit`
- Status: `active`, `archived`, `deleted`
- Difficulty: `trivial`, `easy`, `medium`, `hard`
- PK: `HOUSEHOLD#{household_id}`, SK: `SUBJECT#{subject_id}#HABIT#{habit_id}`

### HabitEvent

- Single log entry for a habit within a time period
- Fields: `id`, `household_id`, `subject_id`, `habit_id`, `period_key`, `status`, `note`, `date_created`, `date_modified`
- Status: `done`, `skipped`, `failed`
- Period keys:
  - Daily: `YYYY-MM-DD` (e.g., `2026-02-13`)
  - Weekly: `YYYY-Www` (e.g., `2026-W07`)
  - Monthly: `YYYY-MM` (e.g., `2026-02`)
- **One event per habit per period** (enforced via deterministic SK)
- PK: `HOUSEHOLD#{household_id}`, SK: `SUBJECT#{subject_id}#HABIT#{habit_id}#EVENT#{period_key}`

### BlogPost

- Personal notes and reflections
- Fields: `id`, `household_id`, `subject_id`, `title`, `content`, `status`, `visibility`, `date_created`, `date_modified`
- Status: `draft`, `published`, `archived`
- Visibility: `private`, `public`
- PK: `HOUSEHOLD#{household_id}`, SK: `SUBJECT#{subject_id}#BLOG#{blog_id}`

---

## 6. Habit Event Rules

### Creation Endpoint

```
POST /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events
```

### Period Key Generation

- **Daily habits**: `YYYY-MM-DD` (e.g., `2026-02-13`)
- **Weekly habits**: `YYYY-Www` (e.g., `2026-W07` for week 7)
- **Monthly habits**: `YYYY-MM` (e.g., `2026-02`)

### Idempotency

- One event per habit per period
- Enforced via deterministic SK construction
- Duplicate requests update the same record
- No conditional writes needed (PUT is naturally idempotent)

---

## 7. Lambda Functions (Current)

### ToDo Operations (5 functions)

- `create-todo`: POST /households/{id}/subjects/{id}/todos
- `get-todo`: GET /households/{id}/subjects/{id}/todos/{id}
- `get-all-todo`: GET /households/{id}/subjects/{id}/todos
- `update-todo`: PUT /households/{id}/subjects/{id}/todos/{id}
- `delete-todo`: DELETE /households/{id}/subjects/{id}/todos/{id}

### Habit Operations (4 functions)

- `create-habit`: POST /households/{id}/subjects/{id}/habits
- `get-habit`: GET /households/{id}/subjects/{id}/habits/{id}
- `get-all-habit`: GET /households/{id}/subjects/{id}/habits
- `update-habit`: PUT /households/{id}/subjects/{id}/habits/{id}

### Habit Event Operations (1 function)

- `create-habit-event`: POST /households/{id}/subjects/{id}/habits/{id}/events

### Blog Operations (4 functions)

- `create-blog`: POST /households/{id}/subjects/{id}/blogs
- `get-blog`: GET /households/{id}/subjects/{id}/blogs/{id}
- `get-all-blog`: GET /households/{id}/subjects/{id}/blogs
- `update-blog`: PUT /households/{id}/subjects/{id}/blogs/{id}

### Authentication (3 functions)

- `signup`: POST /auth/signup
- `login`: POST /auth/login
- `confirm-signup`: POST /auth/confirm

### User Profile (2 functions)

- `create-user-profile`: POST /user-profile
- `get-user-profile`: GET /user-profile

**Total: 19 Lambda functions**

---

## 8. Error Handling

### Error Hierarchy

```
BaseError (500)
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

---

## 9. Technology Stack

### Runtime & Language

- **Python 3.13**
- Type hints with mypy-boto3

### AWS Services

- **Lambda**: Compute (Python 3.13 runtime)
- **API Gateway**: HTTP API with JWT authorizer
- **DynamoDB**: Single table, on-demand billing
- **Cognito**: User Pool for authentication
- **CloudWatch**: Logs and metrics

### Infrastructure

- **Terraform**: Infrastructure as code
- **Modular design**: cognito, dynamodb, api, lambda modules
- **S3**: Terraform state backend

### Dependencies

- `boto3`: AWS SDK
- `dataclasses-json`: Model serialization
- `mypy-boto3-*`: Type hints for AWS services
- `pytest`: Testing framework

### Development Tools

- **Makefile**: Incremental builds and deployment
- **Docker**: Lambda layer compilation (Python 3.13)
- **Virtual environment**: `.venv` for local development

---

## 10. Deployment

### Environments

- `dev`: Development environment
- `prod`: Production environment

### Deployment Commands

```bash
# Full deployment
make deploy ENV=dev

# Deploy single Lambda
make deploy-create-todo ENV=dev

# Rebuild Lambda layer
make rebuild-layer ENV=dev

# Full reset
make nuke && make deploy ENV=dev
```

### Build Artifacts

- Location: `terraform/builds/`
- Lambda zips: `self-growth-{function}-{env}.zip`
- Layer zip: `python.zip`
- Incremental builds: Only rebuilds changed artifacts

---

## 11. Request Flow Example

### Creating a ToDo

1. **Client Request**:

   ```
   POST /households/h123/subjects/s456/todos
   Authorization: Bearer <jwt-token>
   Body: { "title": "Buy groceries", "difficulty": "easy" }
   ```

2. **API Gateway**:
   - Validates JWT token
   - Extracts claims
   - Routes to `create-todo` Lambda

3. **Handler** (`CreateToDoHandler`):
   - Creates `RequestContext` from event
   - Shares context with `ToDoController`
   - Handles errors with full context logging

4. **Controller** (`ToDoController`):
   - Uses `RequestContext` for data access
   - Validates input via `validate_todo_data()`
   - Extracts `household_id`, `subject_id` from path
   - Calls `ToDoService.create()` with validated data

5. **Service** (`ToDoService`):
   - Validates user is household member
   - Validates subject exists in household
   - Creates `ToDo` entity with timestamps
   - Calls `ToDoRepository.create()`

6. **Repository** (`ToDoRepository`):
   - Constructs DynamoDB item with composite key
   - Writes to DynamoDB via `DynamodbService`

7. **Response**:
   ```json
   {
     "statusCode": 201,
     "body": {
       "id": "todo789",
       "title": "Buy groceries",
       "difficulty": "easy",
       "status": "active",
       ...
     }
   }
   ```

---

## 12. Design Patterns

### Shared RequestContext

- Created once in Handler
- Shared with Controller
- Lazy-loaded properties
- Cached for performance
- Single source of truth

### Single Validation Point

- Controllers validate input
- Services receive pre-validated data
- No duplicate validation logic

### Authorization in Services

- Every service method checks membership
- Prevents security bypasses
- Consistent enforcement

### Deterministic Keys

- Same action = same DynamoDB key
- Idempotent by design
- Prevents duplicates

### Error Handling

- Specific error types with HTTP status codes
- Full context logging
- Standardized error responses

---

## 13. Non-Goals (Explicit)

- ❌ No GraphQL (REST only)
- ❌ No ORM (direct DynamoDB access)
- ❌ No framework-heavy runtime (keep cold starts low)
- ❌ No multi-region replication (not yet)
- ❌ No premature abstraction (YAGNI principle)

---

## 14. Status

This document reflects the backend as of **February 2026**.

**Current Version**: Habit Events v1 + Blog Posts + Comprehensive Validation

**Last Updated**: 2026-02-13
