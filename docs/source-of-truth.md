# SOURCE OF TRUTH — Self-Growth Backend

**Version**: 1.0  
**Last Updated**: February 16, 2026  
**Status**: Production Ready

This document is the canonical reference for the **current state** of the Self-Growth backend.
If something conflicts with this file, this file wins.

---

## 1. Purpose

Self-Growth is a **personal development platform** that supports:

- **ToDos**: Task management with checklists, due dates, difficulty levels, and status tracking
- **Habits**: Build or quit habits with daily/weekly/monthly tracking and analytics
- **Habit Events**: Deterministic event logging per time period with streak tracking
- **Blog Posts**: Personal notes and reflections with visibility controls
- **Multi-user households**: Shared accounts with role-based membership management
- **Multiple tracked subjects**: Self, children, dependents, elders, pets
- **Secure, multi-tenant access control**: Household-scoped data isolation with authorization enforcement
- **Pagination & Filtering**: Efficient data retrieval with status filtering
- **Input Sanitization**: XSS and injection attack prevention
- **Rate Limiting**: API throttling with monitoring and alarms

The backend is built to support **shared devices, caregiving use cases, long-term analytics, and production-scale mobile applications**.

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

### Habit Operations (5 functions)

- `create-habit`: POST /households/{id}/subjects/{id}/habits
- `get-habit`: GET /households/{id}/subjects/{id}/habits/{id}
- `get-all-habit`: GET /households/{id}/subjects/{id}/habits
- `update-habit`: PUT /households/{id}/subjects/{id}/habits/{id}
- `delete-habit`: DELETE /households/{id}/subjects/{id}/habits/{id}

### Habit Event Operations (4 functions)

- `create-habit-event`: POST /households/{id}/subjects/{id}/habits/{id}/events
- `get-habit-event`: GET /households/{id}/subjects/{id}/habits/{id}/events/{periodKey}
- `get-all-habit-events`: GET /households/{id}/subjects/{id}/habits/{id}/events
- `get-habit-analytics`: GET /households/{id}/subjects/{id}/habits/{id}/analytics

### Blog Operations (4 functions)

- `create-blog`: POST /households/{id}/subjects/{id}/blogs
- `get-blog`: GET /households/{id}/subjects/{id}/blogs/{id}
- `get-all-blog`: GET /households/{id}/subjects/{id}/blogs
- `update-blog`: PUT /households/{id}/subjects/{id}/blogs/{id}

### Authentication (4 functions)

- `signup`: POST /auth/signup
- `login`: POST /auth/login
- `confirm-signup`: POST /auth/confirm
- `refresh-token`: POST /auth/refresh

### User Profile (2 functions)

- `create-user-profile`: POST /user-profile
- `get-user-profile`: GET /user-profile

### Household Operations (5 functions)

- `create-household`: POST /households
- `get-household`: GET /households/{id}
- `get-all-households`: GET /households
- `update-household`: PUT /households/{id}
- `delete-household`: DELETE /households/{id}

### Household Member Operations (3 functions)

- `create-member`: POST /households/{id}/members
- `get-all-members`: GET /households/{id}/members
- `delete-member`: DELETE /households/{id}/members/{userId}

### Household Subject Operations (5 functions)

- `create-subject`: POST /households/{id}/subjects
- `get-subject`: GET /households/{id}/subjects/{id}
- `get-all-subjects`: GET /households/{id}/subjects
- `update-subject`: PUT /households/{id}/subjects/{id}
- `delete-subject`: DELETE /households/{id}/subjects/{id}

**Total: 37 Lambda functions**

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
- `prod`: Production environment (ready for mobile app integration)

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

# Check AWS credentials before deployment
make check-aws-credentials
```

### Build Artifacts

- Location: `terraform/builds/`
- Lambda zips: `self-growth-{function}-{env}.zip`
- Layer zip: `python.zip`
- Incremental builds: Only rebuilds changed artifacts

### Prerequisites

- AWS CLI configured with valid credentials
- Terraform >= 1.0
- Docker (for Lambda layer compilation)
- Python 3.13
- Make

---

## 11. Security Features

### Input Sanitization

All user input is automatically sanitized to prevent security vulnerabilities:

- **XSS Prevention**: HTML tags and script content stripped
- **HTML Injection Prevention**: Special characters escaped
- **Null Byte Removal**: Null bytes removed from all input
- **Length Limits**: Maximum field lengths enforced
- **Whitespace Normalization**: Leading/trailing whitespace removed

See `docs/input-sanitization.md` for complete details.

### Rate Limiting

API Gateway throttling protects against abuse:

- **Burst Limit**: 100 concurrent requests
- **Rate Limit**: 50 requests/second (steady state)
- **Response**: 429 Too Many Requests when exceeded
- **Monitoring**: CloudWatch alarms for 4xx/5xx errors

See `docs/rate-limiting.md` for retry strategies and monitoring.

### CORS Configuration

Properly configured for mobile/web applications:

- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Authorization, Content-Type, X-Api-Key
- **Exposed Headers**: Content-Length, Date
- **Credentials**: Supported
- **Max Age**: 300 seconds

### Authorization Enforcement

Every service method validates:

1. User is a member of the household
2. Subject exists within the household
3. User has permission for the requested action

This prevents path parameter spoofing and unauthorized access.

---

## 11. Request Flow Example

### Creating a ToDo

1. **Client Request**:

   ```http
   POST /households/h123/subjects/s456/todos
   Authorization: Bearer <jwt-token>
   Content-Type: application/json

   {
     "title": "Buy groceries",
     "difficulty": "easy"
   }
   ```

2. **API Gateway**:
   - Validates JWT token via Cognito authorizer
   - Extracts claims (user_id from sub)
   - Routes to `create-todo` Lambda
   - Applies rate limiting (50 req/sec)

3. **Handler** (`CreateToDoHandler`):
   - Creates `RequestContext` from event
   - Shares context with `ToDoController`
   - Handles errors with full context logging
   - Returns standardized response with CORS headers

4. **Controller** (`ToDoController`):
   - Uses `RequestContext` for data access
   - Validates and sanitizes input via `validate_todo_data()`
   - Strips HTML tags, escapes special characters
   - Extracts `household_id`, `subject_id` from path
   - Calls `ToDoService.create()` with validated data

5. **Service** (`ToDoService`):
   - Validates user is household member via `AccessService`
   - Validates subject exists in household
   - Creates `ToDo` entity with timestamps and IDs
   - Calls `ToDoRepository.create()`

6. **Repository** (`ToDoRepository`):
   - Constructs DynamoDB item with composite key
   - PK: `HOUSEHOLD#{household_id}`
   - SK: `SUBJECT#{subject_id}#TODO#{todo_id}`
   - Writes to DynamoDB via `DynamodbService`

7. **Response**:
   ```json
   {
     "id": "todo789",
     "householdId": "h123",
     "subjectId": "s456",
     "title": "Buy groceries",
     "difficulty": "easy",
     "status": "active",
     "dateCreated": "2026-02-16T10:00:00Z",
     "dateModified": "2026-02-16T10:00:00Z"
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

This document reflects the backend as of **February 16, 2026**.

**Current Version**: 1.0 - Production Ready

**Feature Completeness**: 90%

### Implemented Features ✅

- ✅ Authentication (signup, login, confirm, refresh)
- ✅ User profiles (create, get, update)
- ✅ Households (full CRUD)
- ✅ Household members (add, list, remove)
- ✅ Household subjects (full CRUD)
- ✅ ToDos (full CRUD with pagination)
- ✅ Habits (full CRUD with pagination)
- ✅ Habit events (create, get, list with pagination)
- ✅ Habit analytics (streaks, completion rate, distribution)
- ✅ Blog posts (full CRUD with pagination)
- ✅ Input sanitization (XSS prevention)
- ✅ Rate limiting (API Gateway throttling)
- ✅ CORS configuration
- ✅ Error handling with specific error types
- ✅ Pagination and filtering
- ✅ CloudWatch monitoring and alarms
- ✅ Comprehensive documentation

### Pending Features 🔄

- 🔄 Unit tests (framework exists, tests needed)
- 🔄 Integration tests
- 🔄 Structured logging (basic logging exists)
- 🔄 Load testing

### Future Enhancements 🔮

- 🔮 Notifications (SNS/SES)
- 🔮 AI-powered insights
- 🔮 Multi-region deployment
- 🔮 Caching layer (Redis/ElastiCache)
- 🔮 GraphQL API (optional)
- 🔮 WebSocket support for real-time updates

**Last Updated**: 2026-02-16

---

## 15. Frontend Integration Guide

### Quick Start for Frontend Developers

1. **Authentication Flow**:
   - Sign up → Confirm → Login → Get tokens
   - Store `accessToken` and `refreshToken` securely
   - Include `Authorization: Bearer {accessToken}` in all requests
   - Refresh token when access token expires (24 hours)

2. **Data Hierarchy**:
   - User → Household → Subject → Entity (Todo/Habit/Blog)
   - Always include `householdId` and `subjectId` in paths
   - List user's households first, then subjects, then entities

3. **Error Handling**:
   - Check HTTP status code
   - Parse error response: `{ error, message, details }`
   - Handle 401 (refresh token), 403 (unauthorized), 429 (rate limit)

4. **Pagination**:
   - Use `limit` query param (default: 20, max: 100)
   - Use `nextToken` from response for next page
   - Filter by `status` query param

5. **Input Validation**:
   - Backend sanitizes all input automatically
   - Still validate on frontend for UX
   - See field length limits in API reference

### Example Integration (React Native)

```javascript
// Authentication
const signup = async (email, password) => {
  const response = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return response.json();
};

// Create Todo
const createTodo = async (householdId, subjectId, data) => {
  const response = await fetch(
    `${API_BASE}/households/${householdId}/subjects/${subjectId}/todos`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    },
  );
  return response.json();
};

// List Todos with Pagination
const listTodos = async (householdId, subjectId, nextToken = null) => {
  const params = new URLSearchParams({
    limit: 20,
    status: "active",
    ...(nextToken && { nextToken }),
  });

  const response = await fetch(
    `${API_BASE}/households/${householdId}/subjects/${subjectId}/todos?${params}`,
    {
      headers: { Authorization: `Bearer ${accessToken}` },
    },
  );
  return response.json();
};
```

### Testing Endpoints

Use the provided Postman collection or curl:

```bash
# Sign up
curl -X POST https://api.example.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Login
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"Test123!"}'

# Create Todo
curl -X POST https://api.example.com/households/{id}/subjects/{id}/todos \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","difficulty":"easy"}'
```

---

## 16. Documentation Index

### For Developers

- **SOURCE_OF_TRUTH.md** (this file) - Current state reference
- **PROJECT_CONTEXT.md** - Design principles and mental model
- **ARCHITECTURE_OVERVIEW.md** - System architecture details
- **API_REFERENCE.md** - Complete API endpoint documentation

### For Operations

- **DEPLOYMENT_TROUBLESHOOTING.md** - Common deployment issues
- **RATE_LIMITING.md** - Rate limiting configuration and monitoring
- **INFRASTRUCTURE_AND_DEPLOYMENT.md** - Terraform and AWS setup

### For Security

- **INPUT_SANITIZATION.md** - Security measures and validation
- **SECURITY_QUICK_REFERENCE.md** - Quick security guide
- **REQUEST_CONTEXT_ARCHITECTURE.md** - Request handling patterns

### For Features

- **DOMAIN_MODEL_AND_ENTITIES.md** - Data models and relationships
- **SERVICE_AND_REPOSITORY_REFERENCE.md** - Service layer patterns
- **ROADMAP.md** - Feature roadmap and progress

---
