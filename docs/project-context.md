# PROJECT CONTEXT — Self-Growth

This document defines **how to think** about the Self-Growth project.
It is not implementation detail — it is design intent.

---

## 1. Vision

Self-Growth is a **human-first personal development system** designed for:

- Individuals tracking personal growth
- Families managing shared goals
- Caregivers supporting dependents
- Shared devices with multi-user support
- Long-term habit and behavior tracking with analytics

The app should work just as well for:

- A single person tracking habits and todos
- A parent tracking a child's development
- Someone caring for an elderly parent
- A household managing shared responsibilities

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

### Implemented Features

- ✅ Authentication (signup, login, confirm)
- ✅ User profiles
- ✅ Households and membership
- ✅ Subjects
- ✅ ToDos (full CRUD)
- ✅ Habits (full CRUD)
- ✅ Habit events (create)
- ✅ Blog posts (full CRUD)
- ✅ Shared RequestContext pattern
- ✅ Comprehensive error handling
- ✅ Input validation framework

### Current Focus

- Solid foundations for core entities
- Security correctness
- Clean mental model
- Developer experience (incremental builds, clear patterns)

### Future Enhancements

- Habit analytics and streaks
- Notifications and reminders
- AI-powered insights
- Multi-region deployment
- Caching layer (Redis/ElastiCache)

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
