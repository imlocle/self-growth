# PROJECT CONTEXT — Self-Growth

This document defines **how to think** about the Self-Growth project.
It is not implementation detail — it is design intent.

---

## 1. Vision

Self-Growth is a **human-first personal development system** designed for:

- Individuals
- Families
- Caregivers
- Shared devices
- Long-term habit and behavior tracking

The app should work just as well for:

- A single person tracking habits
- A parent tracking a child
- Someone caring for an elderly parent

---

## 2. Core Design Principles

### 1. Explicit Ownership

Every piece of data belongs to:
User → Household → Subject → Entity

Nothing is global. Nothing is implicit.

---

### 2. Separation of Identity vs Profile

- **Cognito User** = authentication
- **UserProfile** = application identity

This allows:

- Multiple profiles per user
- Shared devices
- Future caregiver permissions

---

### 3. Service Layer Is Law

- Authorization lives in services
- Controllers never decide access
- Repositories never decide meaning

---

### 4. Time Is a First-Class Concept

Habits are not static:

- They repeat
- They streak
- They reset
- They fail

Events exist so the system can answer:

- “How often?”
- “How consistent?”
- “What changed?”

---

### 5. Deterministic Data

If two requests represent the same real-world action:

- They should map to the same DynamoDB key
- The system should be idempotent by default

---

## 3. Mental Model

### Household

A shared container:

- Family
- Couple
- Care group

### Subject

An individual being tracked:

- You
- Your child
- Your parent
- A dependent

### Habit

The _definition_ of intent.

### HabitEvent

The _proof_ of action.

---

## 4. Security Philosophy

- Assume path parameters can be guessed
- Assume clients are hostile
- Never trust frontend-provided IDs
- Always validate ownership via membership tables

---

## 5. API Philosophy

- REST, not RPC
- Path params define scope
- Query params define filtering
- Body defines intent

Example:
POST /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events

---

## 6. Why This Architecture

This architecture was chosen to:

- Scale gradually
- Avoid premature abstraction
- Keep Lambda cold starts low
- Be understandable without tribal knowledge

---

## 7. Current Focus

- Solid ToDo & Habit foundations
- Habit event tracking
- Security correctness
- Clean mental model

AI features come later.

---

## 8. How to Use This Document

In any future discussion:

> “Assume PROJECT_CONTEXT.md”

Means:

- Do not suggest conflicting patterns
- Do not re-litigate architecture
- Build forward, not sideways
