# Architecture Overview

**Self-Growth Backend** is built on a **serverless, event-driven architecture** using AWS services and Python for compute logic. This document describes the system design, components, and patterns.

**Last Updated:** March 12, 2026

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Layered Architecture](#layered-architecture)
3. [AWS Infrastructure](#aws-infrastructure)
4. [Data Models](#data-models)
5. [Request Flow](#request-flow)
6. [Security](#security)
7. [Performance & Scalability](#performance--scalability)

---

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│  Client Applications (Web, Mobile, Desktop)             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
         ┌───────────▼──────────┐
         │   API Gateway        │ Routes & JWT Authorization
         │   (HTTP API)         │
         │                      │
         │  POST /auth/login    │
         │  POST /habits/create │
         │  GET /todos          │
         │  etc. (37 endpoints) │
         └────────┬─────────────┘
                  │
      ┌───────────┴────────────────────┐
      │  Create/Route to Lambda        │
      │  Based on Handler Type         │
      └───────┬──────────────┬──────┬──┴────────┬─────────┐
              │              │      │           │         │
         ┌────▼──┐   ┌──────▼──┐ ┌─▼────┐ ┌───▼──┐  ┌───▼──┐
         │ Auth  │   │ Habits  │ │Todos │ │House-│  │Blog  │
         │Lambda │   │Lambdas  │ │Lambda│ │holds │  │Lambda│
         └────┬──┘   └────┬────┘ └─┬────┘ │Lambda│  └───┬──┘
              │           │        │      └──┬───┘      │
              │  (All Route to 3 Layers)    │          │
              │                              │          │
    ┌─────────▼──┬──────────▬────────────────┼──────────▼─┐
    │ Controllers│ Services │  Repositories  │ (Handlers) │
    └─────────┬──┴──────────┼────────────────┼────────────┘
              │  (Serialize)│  (Persist)     │
              │        ┌────▼────────────────▼─┐
              │        │   AWS DynamoDB Table  │
              │        │   (self_growth)       │
              │        │   Single-Table Design │
              │        └───────────────────────┘
              │
              ├─→ AWS Cognito (JWT Verification)
              ├─→ CloudWatch (Logging & Metrics)
              └─→ Error Response (JSON format)
```

---

## Layered Architecture

Request processing follows a **layered, separation-of-concerns architecture**:

### 1. **Handler Layer** (Lambda Entry Points)

**Location:** `src/handlers/`

Responsibilities:

- Parse Lambda event from API Gateway
- Extract authentication context (JWT claims from Cognito)
- Route to appropriate controller
- Catch exceptions and return HTTP responses

**Handlers by type:**

- `auth/` — Authentication endpoints
- `habits/` — Habit CRUD and analytics
- `habit_events/` — Event tracking
- `todos/` — Todo management
- `blog_posts/` — Blog post operations
- `households/` — Household management
- `household_members/` — Member management
- `household_subjects/` — Subject tracking

**Example Flow:**

```python
def lambda_handler(event, context):
    # Parse API Gateway event
    body = json.loads(event.get("body", "{}"))

    # Extract user context
    claims = event["requestContext"]["authorizer"]["claims"]
    user_id = claims["sub"]

    # Route to controller
    controller = HabitController(services)
    response = controller.create_habit(body, user_id)

    # Return HTTP response
    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
```

### 2. **Controller Layer** (Request Handling)

**Location:** `src/controllers/`

Responsibilities:

- Validate incoming requests
- Sanitize user input (XSS prevention, injection protection)
- Call service layer for business logic
- Format and return responses
- Handle validation errors

**Controllers:**

- `AuthController` — JWT token management
- `HabitController` — Habit operations
- `TodoController` — Todo operations
- `BlogPostController` — Blog post operations
- `HouseholdController` — Household operations
- `UserProfileController` — User preferences

**Example:**

```python
class HabitController(BaseController):
    def create_habit(self, data, user_id):
        # Validate input
        validated = validate_habit_data(data)

        # Call service
        habit = self.habit_service.create(
            user_id=user_id,
            title=validated["title"],
            habit_type=validated["type"]
        )

        # Return formatted response
        return habit.to_dict()
```

### 3. **Service Layer** (Business Logic)

**Location:** `src/services/`

Responsibilities:

- Implement domain-specific business logic
- Coordinate between repositories
- Handle authorization and access control
- Calculate analytics (habit streaks, completion rates)
- Apply business rules and constraints

**Services:**

- `AuthService` — Authentication workflows
- `HabitService` — Habit creation, modification, deletion
- `HabitAnalyticsService` — Streak calculation and metrics
- `TodoService` — Todo management
- `BlogPostService` — Blog post operations
- `HouseholdService` — Multi-user account management
- `AccessService` — Authorization enforcement

**Example:**

```python
class HabitService:
    def create(self, user_id, title, habit_type):
        # Check authorization
        self.access_service.check_ownership(user_id)

        # Apply business logic
        habit = Habit(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            type=habit_type,
            streak=0,
            status="active"
        )

        # Persist
        return self.habit_repo.create(habit)

    def get_analytics(self, habit_id):
        # Calculate streaks
        events = self.habit_event_repo.get_by_habit(habit_id)
        streak = calculate_streak(events)
        completion_rate = calculate_completion_rate(events)

        return {
            "streak": streak,
            "completion_rate": completion_rate
        }
```

### 4. **Repository Layer** (Data Persistence)

**Location:** `src/repositories/`

Responsibilities:

- Abstract database interactions
- Provide CRUD operations on DynamoDB
- Handle query patterns and filtering
- Manage pagination
- No business logic (just data access)

**Repositories:**

- `HabitRepository` — Habit CRUD
- `TodoRepository` — Todo CRUD
- `HabitEventRepository` — Event tracking
- `UserProfileRepository` — User preferences
- `HouseholdRepository` — Household data
- `HouseholdMemberRepository` — Member data

**Example:**

```python
class HabitRepository:
    def create(self, habit):
        return self.dynamodb.put(
            "self_growth",
            habit.to_dynamo()
        )

    def get(self, habit_id):
        item = self.dynamodb.get(
            "self_growth",
            {"PK": f"HABIT#{habit_id}"}
        )
        return Habit.from_dynamo(item) if item else None

    def query_by_user(self, user_id, limit=20, offset=None):
        items = self.dynamodb.query(
            "self_growth",
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": f"USER#{user_id}"}
        )
        return [Habit.from_dynamo(item) for item in items]
```

### 5. **Model Layer** (Domain Entities)

**Location:** `src/models/`

Responsibilities:

- Define domain entities
- Handle serialization (Python object ↔ JSON ↔ DynamoDB format)
- Validate model state
- Provide type hints for IDE support

**Models:**

- `Habit` — Habit tracking entity
- `Todo` — Task management entity
- `BlogPost` — Blog post entity
- `User` — User identity (Cognito-managed)
- `Household` — Shared account entity
- `HouseholdMember` — Member of household
- `HabitEvent` — Habit occurrence/event

**Example:**

```python
@dataclass
class Habit:
    id: str
    user_id: str
    title: str
    type: HabitType  # Enum: BUILD or QUIT
    counter: CounterType  # DAILY, WEEKLY, MONTHLY
    streak: int
    status: HabitStatus  # ACTIVE, ARCHIVED, DELETED

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type.value,
            "streak": self.streak,
            "status": self.status.value
        }

    def to_dynamo(self):
        return {
            "PK": f"HABIT#{self.id}",
            "SK": f"USER#{self.user_id}",
            "GSI1PK": f"USER#{self.user_id}",
            "GSI1SK": f"HABIT#{self.id}",
            "entity": "Habit",
            "title": self.title,
            "type": self.type.value,
            "streak": self.streak,
            "status": self.status.value,
            "date_created": self.date_created.isoformat(),
            "date_modified": self.date_modified.isoformat()
        }
```

---

## AWS Infrastructure

### API Gateway (HTTP API)

**Purpose:** Route HTTP requests to Lambda functions with authentication

**Configuration:**

- **Type:** HTTP API (not REST API, faster and cheaper)
- **Stage:** `/prod`, `/staging` (environment-based)
- **Authorizer:** JWT verification from Cognito
- **CORS:** Enabled for web clients
- **Throttling:** Rate limits per API key/IP

**Request Flow:**

1. Client sends HTTPS request to `https://api.example.com/habits`
2. API Gateway verifies JWT token via Cognito
3. Extracts claims and adds to Lambda event context
4. Routes to appropriate Lambda function
5. Lambda returns response (200, 400, 500, etc.)
6. API Gateway formats and returns to client

### Lambda Functions (37 total)

**Purpose:** Serverless compute layer executing business logic

**Configuration:**

- **Runtime:** Python 3.13
- **Memory:** 256-512 MB (depends on function complexity)
- **Timeout:** 30 seconds (default, adjustable per function)
- **Layers:** Shared dependencies (boto3, dataclasses-json, etc.)
- **Environment Variables:** Database table names, Cognito settings

**Function Organization by Handler:**

- `auth/` (4 functions): Login, signup, refresh, confirm
- `habits/` (8 functions): Create, get, list, update, delete, get_analytics, event operations
- `todos/` (6 functions): CRUD operations, checklist management
- `blog_posts/` (4 functions): CRUD operations
- `households/` (8 functions): CRUD, member management, subject management
- `user_profiles/` (7 functions): Preferences, settings

**Permissions (IAM Roles):**

```yaml
Lambda Role Permissions:
  - dynamodb:PutItem (create/update)
  - dynamodb:GetItem (read)
  - dynamodb:Query (list with filters)
  - dynamodb:DeleteItem (archive/soft delete)
  - dynamodb:UpdateItem (modify)
  - logs:CreateLogGroup, logs:CreateLogStream (CloudWatch logging)
  - cognito-idp:AdminGetUser (user verification)
  - kms:Decrypt (if environment variables are encrypted)
```

### DynamoDB (Single-Table Design)

**Purpose:** Serverless, fully managed NoSQL database

**Table Configuration:**

- **Table Name:** `self_growth`
- **Primary Key:**
  - **PK (Partition Key):** Composite: `USER#{user_id}` or `HABIT#{habit_id}`
  - **SK (Sort Key):** Composite: `METADATA` or resource type
- **Billing Mode:** PAY_PER_REQUEST (auto-scale)
- **Attributes:**
  - `entity` (discriminator): Habit, Todo, User, etc.
  - `date_created`, `date_modified` (timestamps)
  - `date_gsi1`, `date_gsi2` (for time-based queries)
- **Global Secondary Indexes (GSIs):**
  - **GSI1:** `GSI1PK` (User) → `GSI1SK` (Timestamp) — recent items per user
  - **GSI2:** `GSI2PK` (Status) → `GSI2SK` (Timestamp) — global queries

**Access Patterns:**
| Query | Example | Efficiency |
|-------|---------|-----------|
| Get user's habits | `PK = USER#{id}` | O(1) direct lookup |
| List user's todos | `GSI1PK = USER#{id}` | O(1) + scan items |
| Get habit analytics | `PK = HABIT#{id}` + events | O(n) with n = event count |
| Recent items | `GSI1PK = USER#{id}, GSI1SK > date` | O(1) + filtered items |

**Item Structure Example (Habit):**

```json
{
  "PK": "HABIT#550e8400-e29b",
  "SK": "USER#user123",
  "GSI1PK": "USER#user123",
  "GSI1SK": "2026-03-12T10:30:00Z",
  "entity": "Habit",
  "id": "550e8400-e29b",
  "user_id": "user123",
  "title": "Morning Exercise",
  "type": "BUILD",
  "counter": "DAILY",
  "streak": 15,
  "status": "ACTIVE",
  "date_created": "2026-01-15T08:00:00Z",
  "date_modified": "2026-03-12T10:30:00Z"
}
```

### Cognito User Pool

**Purpose:** Managed user authentication and identity

**Configuration:**

- **User Attributes:** Email, first_name, last_name, phone_number
- **Password Policy:** Min 8 chars, uppercase, lowercase, number, special char
- **MFA:** Optional (email/SMS)
- **Session:** 1 hour access token, 30 days refresh token
- **Token Format:** JWT with user claims (sub, email, custom attributes)

**JWT Token Structure:**

```json
{
  "sub": "user123",
  "email": "user@example.com",
  "email_verified": true,
  "given_name": "John",
  "family_name": "Doe",
  "iat": 1678601400,
  "exp": 1678605000
}
```

### CloudWatch (Logging & Monitoring)

**Purpose:** Centralized logging, metrics, and alarms

**Configuration:**

- **Log Groups:** `/aws/lambda/function-name` per function
- **Log Stream:** One per Lambda invocation
- **Log Retention:** 30 days (configurable)
- **Metrics:**
  - `Duration` — execution time
  - `Errors` — count of failed invocations
  - `Throttles` — rate limit hits
  - `ConcurrentExecutions` — active functions

**Alarms:**

- High error rate (>5% of invocations)
- High duration (>20s per invocation)
- DynamoDB throttling
- Cognito failures

---

## Data Models

### Core Entities

#### Habit

Represents a habit to build or quit with tracking.

**Fields:**

- `id` (UUID) — Unique identifier
- `user_id` (string) — Owner
- `title` (string, max 200) — Habit name
- `type` (enum: BUILD | QUIT) — Build habit or quit habit
- `counter` (enum: DAILY | WEEKLY | MONTHLY) — Frequency
- `difficulty` (enum: EASY | MEDIUM | HARD) — Difficulty level
- `streak` (integer) — Current streak count
- `status` (enum: ACTIVE | ARCHIVED | DELETED) — Lifecycle
- `date_created` (timestamp)
- `date_modified` (timestamp)

**Related Data:**

- `HabitEvent[]` — Individual habit occurrences

#### Todo

Represents a task or checklist item.

**Fields:**

- `id` (UUID) — Unique identifier
- `user_id` (string) — Owner
- `title` (string, max 200) — Todo title
- `checklist` (array of items) — Subtasks
- `due_date` (date, optional)
- `difficulty` (enum: EASY | MEDIUM | HARD)
- `status` (enum: ACTIVE | COMPLETED | DELETED)
- `date_created` (timestamp)
- `date_modified` (timestamp)

#### BlogPost

Represents a personal note or blog post.

**Fields:**

- `id` (UUID) — Unique identifier
- `user_id` (string) — Author
- `title` (string, max 200)
- `content` (string, max 10,000)
- `status` (enum: DRAFT | PUBLISHED | ARCHIVED)
- `visibility` (enum: PRIVATE | PUBLIC)
- `date_created` (timestamp)
- `date_modified` (timestamp)

#### Household

Represents a shared account for multiple users.

**Fields:**

- `id` (UUID) — Unique identifier
- `owner_id` (string) — Account owner
- `name` (string, max 100)
- `members` (HouseholdMember[])
- `subjects` (HouseholdSubject[]) — Track self, children, pets, dependents
- `date_created` (timestamp)
- `date_modified` (timestamp)

#### HouseholdMember

Represents a member of a household with role-based access.

**Fields:**

- `id` (UUID)
- `household_id` (UUID)
- `cognito_user_id` (string) — Link to Cognito user
- `display_name` (string)
- `role` (enum: OWNER | ADMIN | MEMBER)
- `access_level` (enum: FULL | LIMITED | VIEW_ONLY)
- `date_created` (timestamp)
- `date_modified` (timestamp)

---

## Request Flow

### Example: Create a Habit

```
1. Client Request
   POST /habits
   Authorization: Bearer eyJhbGc...
   Content-Type: application/json
   {
     "title": "Morning Run",
     "type": "BUILD",
     "counter": "DAILY",
     "difficulty": "MEDIUM"
   }
   ↓

2. API Gateway
   - Verify JWT token with Cognito
   - Extract claims: { sub: "user123", email: "user@example.com" }
   - Route to Lambda: habit_create_handler
   ↓

3. Lambda Handler (src/handlers/habits/create.py)
   - Parse event body
   - Extract user_id from "sub" claim
   - Call HabitController.create_habit()
   ↓

4. Controller (src/controllers/habit_controller.py)
   - Validate input data:
     * title: 1-200 chars, no HTML/scripts
     * type: BUILD or QUIT
     * counter: DAILY, WEEKLY, or MONTHLY
     * difficulty: EASY, MEDIUM, or HARD
   - Sanitize strings (remove XSS vectors)
   - Call HabitService.create()
   ↓

5. Service (src/services/habit_service.py)
   - Check authorization via AccessService
   - Create Habit domain object
   - Call HabitRepository.create()
   ↓

6. Repository (src/repositories/habit_repository.py)
   - Convert Habit → DynamoDB item
   - Call DynamoDB put_item()
   - Return persisted Habit
   ↓

7. Response Flow
   - Repository returns Habit
   - Service returns Habit
   - Controller converts to JSON dict
   - Handler returns HTTP response:
   {
     "statusCode": 201,
     "body": "{\"id\": \"...\", \"title\": \"Morning Run\", ...}"
   }
   - API Gateway returns to client with 201 Created
   ↓

8. Client Response
   HTTP 201 Created
   {
     "id": "550e8400-e29b",
     "title": "Morning Run",
     "type": "BUILD",
     "counter": "DAILY",
     "difficulty": "MEDIUM",
     "streak": 0,
     "status": "ACTIVE",
     "date_created": "2026-03-12T10:30:00Z",
     "date_modified": "2026-03-12T10:30:00Z"
   }
```

---

## Security

### Authentication & Authorization

**JWT Token Flow:**

1. User signs up/logs in via Cognito
2. Cognito returns access_token + refresh_token
3. Client includes access_token in `Authorization: Bearer`
4. API Gateway verifies JWT signature against Cognito public key
5. Extract claims and pass to Lambda

**Role-Based Access Control:**

- Households have members with roles: OWNER, ADMIN, MEMBER
- Access levels: FULL, LIMITED, VIEW_ONLY
- AccessService enforces rules (only owner can delete household)

### Input Validation & Sanitization

**HTML Sanitization:**

- Remove `<script>` and `<style>` tags completely
- Strip remaining HTML tags
- Escape `<`, `>`, `&`, `"`, `'` to HTML entities
- Remove null bytes

**Field Length Limits:**
| Field | Max Length |
|-------|-----------|
| Email | 254 chars |
| Password | 256 chars |
| Username | 50 chars |
| Titles | 200 chars |
| Descriptions | 1,000 chars |
| Blog content | 10,000 chars |

**Validation Rules:**

- Email: RFC 5321 compliant
- Passwords: No validation beyond length (Cognito enforces policy)
- Names/titles: Alphanumeric + spaces + common punctuation
- URLs: Must be valid HTTPS

### Rate Limiting

**Implemented via:**

- API Gateway throttling (5,000 requests/second default)
- Per-user rate limits track failures in CloudWatch
- Suspicious patterns trigger automatic blocks

**Monitored Metrics:**

- Failed login attempts (after 3: account lock for 15 min)
- High error rates per IP
- Unusual access patterns

### Error Handling

**Security-Conscious Error Responses:**

- Don't expose internal details (stack traces never shown to client)
- Generic "Internal Server Error" for 5xx
- Specific validation errors for 4xx (field-level feedback)
- No SQL/database errors leaked

**Example:**

```json
400 Bad Request
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid input for field: title",
  "details": [
    {
      "field": "title",
      "issue": "must be between 1 and 200 characters"
    }
  ]
}
```

---

## Performance & Scalability

### Serverless Auto-Scaling

- **Lambda:** Automatically scales to handle request volume (up to 1,000 concurrent)
- **DynamoDB:** PAY_PER_REQUEST billing auto-scales read/write capacity
- **API Gateway:** Managed by AWS, scales transparently

### Query Optimization

**Single-Table Design Benefits:**

- Fewer table scans (avoid N+1 queries)
- Partition key design groups related data
- GSIs enable common query patterns
- Pagination prevents large result sets

**Example Query Pattern:**

```dynamo
User requests: GET /users/user123/habits?limit=20

Executes:
Query(
  PK = "USER#user123"
  SK between "HABIT#" limits
  limit: 20
)

Result: ~50ms latency, minimal read capacity
```

### Caching Strategy

- **Client-side:** Browser/app HTTP caching (Cache-Control headers)
- **Server-side:** DynamoDB caching via DAX (optional enhancement)
- **No server-side caching layer:** Stateless Lambda keeps deployments simple

### Monitoring & Alarms

**Key Metrics:**

- Lambda duration: Target <1s for standard operations
- DynamoDB read/write units: Monitor throttling
- Error rate: Alert if >1%
- Cold starts: Monitor and optimize

---

## Deployment & Infrastructure

Infrastructure is managed via **Terraform** with modules for:

- **VPC & Networking:** Optional (for private databases)
- **Cognito:** User pool, app client, domain
- **DynamoDB:** Table schema, indexes, billing
- **Lambda:** Functions, layers, roles, permissions
- **API Gateway:** Routes, authorizer, CORS

See [docs-internal/DEPLOYMENT.md](../docs-internal/DEPLOYMENT.md) for Terraform structure and deployment commands.

---

**Last Updated:** March 12, 2026  
**Version:** 1.0  
**Status:** Production Ready
