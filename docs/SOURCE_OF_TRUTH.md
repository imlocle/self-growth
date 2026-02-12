# SOURCE OF TRUTH — Self-Growth Backend

This document is the canonical reference for the **current state** of the Self-Growth backend.
If something conflicts with this file, this file wins.

---

## 1. Purpose

Self-Growth is a **personal development platform** that supports:

- ToDos
- Habits (build or quit)
- Habit Events (daily/weekly/monthly tracking)
- Multi-user households
- Multiple tracked subjects (self, child, dependent, elder, etc.)
- Secure, multi-tenant access control

The backend is built to support **shared devices, caregiving use cases, and long-term analytics**.

---

## 2. Architecture (Authoritative)

### High-level pattern

API Gateway (HTTP API, JWT Authorizer)
→ Lambda Handler
→ Controller
→ Service
→ Repository
→ DynamoDB (Single Table)

### Responsibilities

- **Handler**
  - HTTP wiring
  - Error → response mapping
- **Controller**
  - Parse request (path, query, body)
  - No business logic
- **Service**
  - Authorization
  - Business rules
  - Orchestration
- **Repository**
  - DynamoDB access only
  - No auth, no logic

---

## 3. Authentication & Authorization

### Authentication

- AWS Cognito User Pool
- **Access token** used in API Gateway JWT authorizer
- `sub` claim is the canonical `user_id`
- Email is NOT guaranteed in access token

### Authorization (Critical)

Authorization is enforced in **Service layer**, never in controllers.

Every scoped request validates:

1. User is a **member of the household**
2. Subject exists within the household

This prevents path-parameter spoofing attacks.

---

## 4. DynamoDB Single Table Design

### Partition Key (PK)

| Entity      | PK Pattern               |
| ----------- | ------------------------ |
| UserProfile | AUTHUSER#{user_id}       |
| Household   | HOUSEHOLD#{household_id} |

### Sort Key (SK) patterns

| Entity      | SK Pattern                                               |
| ----------- | -------------------------------------------------------- |
| UserProfile | META#PROFILE                                             |
| Household   | META#HOUSEHOLD                                           |
| Member      | MEMBER#{user_id}                                         |
| Subject     | SUBJECT#{subject_id}                                     |
| ToDo        | SUBJECT#{subject_id}#TODO#{todo_id}                      |
| Habit       | SUBJECT#{subject_id}#HABIT#{habit_id}                    |
| Habit Event | SUBJECT#{subject_id}#HABIT#{habit_id}#EVENT#{period_key} |

### Guarantees

- One Habit Event per period (daily/weekly/monthly)
- Deterministic SKs prevent duplicates
- All data is household-scoped

---

## 5. Core Models (Authoritative)

### UserProfile

Represents a user’s identity within the app.

- Separate from Cognito
- Supports multiple profiles per user in the future

### Household

Represents a shared account / family / care group.

### Subject

Represents an entity being tracked:

- Self
- Child
- Elder
- Dependent

### ToDo

Task scoped to a subject.

### Habit

Definition of a habit:

- Counter: daily / weekly / monthly
- Type: build / quit

### HabitEvent

A single log entry for a habit within a time period.

---

## 6. Habit Event Rules

- HabitEvents are created via:
  POST /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events

- Period keys:

  - Daily → `YYYY-MM-DD`
  - Weekly → `YYYY-Www`
  - Monthly → `YYYY-MM`

- One event per habit per period
- Enforced via DynamoDB conditional writes

---

## 7. Lambdas (Current)

### ToDo

- create-todo
- get-todo
- get-all-todo
- update-todo
- delete-todo

### Habit

- create-habit
- get-habit
- get-all-habit
- update-habit

### Habit Events

- create-habit-event

### Auth

- signup
- login
- confirm-signup

### User Profile

- create-user-profile
- get-user-profile

---

## 8. Non-Goals (Explicit)

- No GraphQL
- No ORM
- No framework-heavy Lambda runtime
- No multi-region replication (yet)

---

## 9. Status

This document reflects the backend as of **Habit Events v1**.
