# PROJECT CONTEXT — Self-Growth

**Version**: 1.0  
**Last Updated**: February 16, 2026  
**Status**: Production Ready

This document defines **how to think** about the Self-Growth project.
It is not implementation detail — it is design intent and architectural philosophy.

---

## 1. Vision

Self-Growth is a **human-first personal development system** designed for:

- Individuals tracking personal growth and habits
- Families managing shared goals and responsibilities
- Caregivers supporting dependents (children, elderly, disabled)
- Shared devices with multi-user support
- Long-term habit and behavior tracking with analytics
- Privacy-first data ownership

The app should work just as well for:

- A single person tracking habits and todos
- A parent tracking a child's development milestones
- Someone caring for an elderly parent's medication and appointments
- A household managing shared responsibilities and chores
- A therapist tracking client progress (future use case)

---

## 2. Core Design Principles

### 1. Explicit Ownership

Every piece of data belongs to:
**User → Household → Subject → Entity**

Nothing is global. Nothing is implicit.

- Users authenticate via Cognito
- Households contain members and subjects
- Subjects are tracked individuals (self, child, dependent)
- Entities (ToDo, Habit, HabitEvent, BlogPost) belong to subjects

---

### 2. Separation of Identity vs Profile

- **Cognito User** = authentication (AWS managed)
- **UserProfile** = application identity (app managed)

This allows:

- Multiple profiles per user (future)
- Shared devices
- Caregiver permissions (future)
- Separation of auth concerns from app data

---

### 3. Service Layer Is Law

Authorization and business logic live in services, never in controllers or repositories.

- **Controllers**: Parse and validate input
- **Services**: Enforce authorization and business rules
- **Repositories**: Data access only

This prevents security bypasses and ensures consistent enforcement.

---

### 4. Shared RequestContext Pattern

RequestContext is the single source of truth for all request data:

- Created once in Handler
- Shared with Controller
- Lazy-loaded and cached
- Eliminates duplicate extraction logic
- Provides full context for error logging

---

### 5. Single Validation Point

Input validation happens in Controllers only:

- Controllers validate and normalize input
- Services receive pre-validated data
- No duplicate validation logic
- Clear separation of concerns

---

### 6. Time Is a First-Class Concept

Habits are not static — they repeat, streak, reset, and fail.

Events exist so the system can answer:

- "How often did this happen?"
- "How consistent was the behavior?"
- "What changed over time?"

Period keys (YYYY-MM-DD, YYYY-Www, YYYY-MM) ensure deterministic tracking.

---

### 7. Deterministic Data

If two requests represent the same real-world action:

- They should map to the same DynamoDB key
- The system should be idempotent by default
- Conditional writes prevent duplicates

Example: Creating a habit event for "today" twice should update the same record.

---

## 3. Mental Model

### User

An authenticated identity (Cognito sub). Can be a member of multiple households.

### UserProfile

Application-level identity with username, email, preferences.

### Household

A shared container representing:

- Family
- Couple
- Care group
- Shared account

### HouseholdMember

Junction entity linking Users to Households with roles.

### Subject

An individual being tracked within a household:

- You (self-tracking)
- Your child
- Your parent
- A dependent

### HouseholdSubject

Junction entity linking Subjects to Households.

### ToDo

A task scoped to a subject with status, difficulty, checklist, due date.

### Habit

The _definition_ of intent:

- Type: build or quit
- Counter: daily, weekly, monthly
- Difficulty: trivial, easy, medium, hard

### HabitEvent

The _proof_ of action:

- One event per habit per period
- Status: done, skipped, failed
- Deterministic period keys

### BlogPost

Personal notes and reflections scoped to a subject with visibility controls.

---

## 4. Security Philosophy

- **Assume path parameters can be guessed**
- **Assume clients are hostile**
- **Never trust frontend-provided IDs**
- **Always validate ownership via membership tables**

Every service method validates:

1. User is a member of the household
2. Subject exists within the household

This prevents path parameter spoofing attacks where a user tries to access another household's data.

---

## 5. API Philosophy

- **REST, not RPC**
- **Path params define scope** (household, subject, entity)
- **Query params define filtering** (status, date range)
- **Body defines intent** (data to create/update)

Example:

```
POST /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events
```

This URL structure enforces the ownership hierarchy and makes authorization explicit.

---

## 6. Why This Architecture

This architecture was chosen to:

- **Scale gradually**: Serverless scales automatically
- **Avoid premature abstraction**: No ORM, no heavy frameworks
- **Keep Lambda cold starts low**: Minimal dependencies, Lambda layers
- **Be understandable without tribal knowledge**: Clear layers, explicit patterns
- **Support multi-tenancy**: Household-scoped data with strong isolation
- **Enable incremental deployment**: Makefile supports single-lambda updates

---

## 7. Current State

### Implemented Features ✅

**Authentication & Authorization**

- ✅ AWS Cognito integration (signup, login, confirm, refresh)
- ✅ JWT token validation via API Gateway
- ✅ Household membership validation
- ✅ Subject ownership validation
- ✅ Path parameter spoofing prevention

**Core Entities**

- ✅ User profiles (create, get, update)
- ✅ Households (full CRUD)
- ✅ Household members (add, list, remove with roles)
- ✅ Household subjects (full CRUD for self/child/adult/pet)
- ✅ ToDos (full CRUD with checklists, due dates, difficulty)
- ✅ Habits (full CRUD with daily/weekly/monthly counters)
- ✅ Habit events (create, get, list with deterministic period keys)
- ✅ Habit analytics (streaks, completion rate, distribution)
- ✅ Blog posts (full CRUD with visibility controls)

**Data Management**

- ✅ Pagination (limit, nextToken for all list endpoints)
- ✅ Filtering (status-based filtering)
- ✅ Sorting (date_modified, date_due for todos)
- ✅ DynamoDB single-table design with efficient queries

**Security**

- ✅ Input sanitization (XSS prevention, HTML stripping)
- ✅ Rate limiting (100 burst, 50 req/sec)
- ✅ CORS configuration for mobile/web apps
- ✅ Field length validation
- ✅ Authorization enforcement in services

**Infrastructure**

- ✅ Terraform IaC (modular design)
- ✅ 37 Lambda functions (Python 3.13)
- ✅ Lambda layers for dependencies
- ✅ Incremental build system (Makefile)
- ✅ CloudWatch logging and alarms
- ✅ Environment separation (dev/prod)

**Developer Experience**

- ✅ Shared RequestContext pattern
- ✅ Comprehensive error handling
- ✅ Type hints with mypy-boto3
- ✅ Single validation point (controllers)
- ✅ Clear layered architecture
- ✅ Extensive documentation

### Current Focus

- Production-ready foundations for core entities
- Security correctness and input validation
- Clean mental model and consistent patterns
- Developer experience (incremental builds, clear patterns)
- Mobile app integration readiness

### Pending Work 🔄

- 🔄 Unit tests (framework exists, tests needed for services/repositories)
- 🔄 Integration tests (end-to-end API flows)
- 🔄 Structured logging (JSON format, request ID tracking)
- 🔄 Load testing (validate performance at scale)

### Future Enhancements 🔮

**Analytics & Insights**

- 🔮 Advanced habit analytics (trends, predictions)
- 🔮 Weekly/monthly progress reports
- 🔮 AI-powered insights and recommendations
- 🔮 Export data (CSV, PDF)

**Notifications**

- 🔮 SNS/SES integration
- 🔮 Push notifications (via mobile app)
- 🔮 Email reminders for todos and habits
- 🔮 SMS reminders (optional)

**Social Features**

- 🔮 Household activity feed
- 🔮 Subject progress sharing
- 🔮 Encouragement messages
- 🔮 Achievements/badges

**Infrastructure**

- 🔮 Multi-region deployment
- 🔮 Redis/ElastiCache for caching
- 🔮 GraphQL API (optional)
- 🔮 WebSocket support for real-time updates
- 🔮 CDN for static assets

---

## 8. How to Use This Document

In any future discussion:

> "Assume PROJECT_CONTEXT.md"

Means:

- Do not suggest conflicting patterns
- Do not re-litigate architecture decisions
- Build forward, not sideways
- Respect the established mental model
- Follow the layered architecture
- Maintain security-first approach

When adding new features:

1. Follow the ownership hierarchy (User → Household → Subject → Entity)
2. Validate in Controller, authorize in Service
3. Use shared RequestContext
4. Create specific error types
5. Follow DynamoDB single-table design patterns
6. Add Lambda handler following established patterns
7. Update Makefile with new Lambda function
8. Add Terraform module for infrastructure
9. Document in API reference
10. Add tests for new functionality

---

## 9. For Frontend Developers

### Understanding the Backend

The Self-Growth backend is a **RESTful API** built on AWS serverless architecture:

- **Stateless**: Each request is independent
- **JWT-based auth**: Include access token in Authorization header
- **Hierarchical URLs**: `/households/{id}/subjects/{id}/todos`
- **Standard HTTP methods**: GET (read), POST (create), PUT (update), DELETE (delete)
- **JSON payloads**: All requests and responses use JSON

### Key Concepts

**Household**: A shared container (family, care group, etc.)

- Users can be members of multiple households
- Each household has members with roles (owner, admin, member)

**Subject**: An individual being tracked within a household

- Types: self, child, adult, pet
- Each subject has their own todos, habits, and blog posts

**Habit Events**: Time-based tracking

- One event per habit per period (day/week/month)
- Period keys are deterministic (e.g., "2026-02-16" for daily)
- Idempotent by design (same request = same result)

### Integration Checklist

1. **Authentication**:
   - Implement signup → confirm → login flow
   - Store access token and refresh token securely
   - Refresh token before expiration (24 hours)
   - Handle 401 errors by refreshing token

2. **Data Fetching**:
   - List user's households first
   - Let user select household
   - List subjects in household
   - Fetch todos/habits/blogs for selected subject

3. **Pagination**:
   - Use `limit` query param (default: 20, max: 100)
   - Store `nextToken` from response
   - Pass `nextToken` to fetch next page
   - Show "Load More" button when `nextToken` exists

4. **Error Handling**:
   - Parse error response: `{ error, message, details }`
   - Show user-friendly messages
   - Handle 429 (rate limit) with exponential backoff
   - Handle 403 (unauthorized) by checking household membership

5. **Offline Support** (recommended):
   - Cache data locally (SQLite, Realm, etc.)
   - Sync changes when online
   - Handle conflicts (last-write-wins or user choice)

### API Patterns

**List Resources**:

```http
GET /households/{id}/subjects/{id}/todos?limit=20&status=active
```

**Create Resource**:

```http
POST /households/{id}/subjects/{id}/todos
Content-Type: application/json
Authorization: Bearer {token}

{"title": "Buy milk", "difficulty": "easy"}
```

**Update Resource**:

```http
PUT /households/{id}/subjects/{id}/todos/{id}
Content-Type: application/json
Authorization: Bearer {token}

{"status": "completed"}
```

**Delete Resource**:

```http
DELETE /households/{id}/subjects/{id}/todos/{id}
Authorization: Bearer {token}
```

### Common Pitfalls

❌ **Don't** hardcode household/subject IDs
✅ **Do** fetch from user's households and let them select

❌ **Don't** assume user has only one household
✅ **Do** support multiple households per user

❌ **Don't** retry failed requests immediately
✅ **Do** implement exponential backoff for retries

❌ **Don't** store passwords or tokens in plain text
✅ **Do** use secure storage (Keychain, Keystore, etc.)

❌ **Don't** trust client-side validation alone
✅ **Do** validate on frontend for UX, backend validates for security

### Testing Your Integration

1. **Sign up a test user**
2. **Confirm email** (check email or use test code)
3. **Login** and store tokens
4. **Create household** (automatically created with profile)
5. **List subjects** (default subject created with profile)
6. **Create todo** for subject
7. **List todos** with pagination
8. **Update todo** status to completed
9. **Create habit** with daily counter
10. **Log habit event** for today
11. **Get habit analytics** to see streak

### Support & Documentation

- **API Reference**: `docs/api-reference.md`
- **Source of Truth**: `docs/source-of-truth.md`
- **Input Sanitization**: `docs/input-sanitization.md`
- **Rate Limiting**: `docs/rate-limiting.md`
- **Deployment Troubleshooting**: `docs/deployment-troubleshooting.md`

---

## 10. Production Readiness Checklist

### Security ✅

- [x] Authentication (Cognito)
- [x] Authorization (household membership)
- [x] Input sanitization (XSS prevention)
- [x] Rate limiting (API Gateway)
- [x] CORS configuration
- [x] Field length validation
- [x] Error handling without leaking sensitive data

### Reliability ✅

- [x] Error handling with specific error types
- [x] Idempotent operations (habit events)
- [x] Deterministic keys (no duplicates)
- [x] CloudWatch logging
- [x] CloudWatch alarms (4xx/5xx errors)
- [ ] Unit tests (>70% coverage) - IN PROGRESS
- [ ] Integration tests - IN PROGRESS
- [ ] Load testing - PENDING

### Observability ✅

- [x] Basic logging (CloudWatch)
- [x] Error tracking (CloudWatch alarms)
- [x] Request ID tracking (RequestContext)
- [ ] Structured logging (JSON format) - PENDING
- [ ] Performance metrics - PENDING
- [ ] Audit trail - PENDING

### Documentation ✅

- [x] Architecture documentation
- [x] API reference (complete)
- [x] Source of truth
- [x] Project context
- [x] Deployment guide
- [x] Security documentation
- [x] Frontend integration guide

### Performance ✅

- [x] Serverless architecture (auto-scaling)
- [x] DynamoDB on-demand billing
- [x] Lambda layers (reduce cold starts)
- [x] Incremental builds (fast deployments)
- [ ] Caching strategy - FUTURE
- [ ] Load testing validation - PENDING

**Overall Status**: 90% Production Ready

**Remaining Work**: Testing (unit, integration, load) and structured logging

---
