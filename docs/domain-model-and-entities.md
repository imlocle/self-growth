# Domain Model and Entities

## Core Domain Concepts

The Self-Growth application is built around personal development tracking for individuals within household contexts. The domain model supports multi-user households, caregiving scenarios, and long-term habit tracking.

## Entity Relationships

```
Household (1) ──→ (many) HouseholdMember
Household (1) ──→ (many) HouseholdSubject
HouseholdSubject (1) ──→ (many) ToDo
HouseholdSubject (1) ──→ (many) Habit
Habit (1) ──→ (many) HabitEvent
```

## Core Entities

### UserProfile

Represents application identity (separate from Cognito authentication).

**Fields:**

- `id` (string): Cognito sub (primary identifier)
- `email` (string): User email address
- `username` (string): Unique username (3-20 chars, alphanumeric + underscore)
- `household_id` (string): Associated household
- `subject_id` (string): Default subject for this user
- `first_name` (string): User's first name
- `last_name` (string): User's last name
- `phone_number` (string): Phone number (10-15 digits)
- `date_created` (datetime): Creation timestamp
- `date_modified` (datetime): Last modification timestamp

**Validation Rules:**

- Username: 3-20 characters, alphanumeric + underscore only
- Email: RFC-compliant email format
- Phone: 10-15 digits only

**Business Rules:**

- One profile per Cognito user
- Supports multiple profiles per user in future iterations

### Household

Shared container for family, couple, or care group.

**Fields:**

- `id` (string): Unique household identifier
- `name` (string): Household display name
- `owner_user_id` (string): User who created the household
- `date_created` (datetime): Creation timestamp
- `date_modified` (datetime): Last modification timestamp

**Business Rules:**

- All application data is scoped to households
- Owner has administrative privileges
- Supports multi-generational families and caregiving scenarios

### HouseholdMember

Represents user membership in a household.

**Fields:**

- `household_id` (string): Household identifier
- `user_id` (string): User identifier
- `role` (string): Member role (owner, member, caregiver)
- `display_name` (string): Name shown within household
- `dob` (date): Date of birth (optional)
- `date_created` (datetime): Membership creation timestamp
- `date_modified` (datetime): Last modification timestamp

**Business Rules:**

- Enforces access control for all household data
- Prevents path-parameter spoofing attacks
- Required for all household-scoped operations

### HouseholdSubject

Individual being tracked (self, child, parent, dependent).

**Fields:**

- `id` (string): Unique subject identifier
- `household_id` (string): Parent household
- `type` (string): Subject type (self, child, parent, dependent)
- `display_name` (string): Subject display name
- `dob` (date): Date of birth (optional)
- `points` (integer): Gamification points (currently paused)
- `level` (integer): Gamification level (currently paused)
- `date_created` (datetime): Creation timestamp
- `date_modified` (datetime): Last modification timestamp

**Business Rules:**

- Scoped to household for privacy
- Supports tracking multiple individuals
- Gamification features available but not active

### ToDo

Task scoped to a subject.

**Fields:**

- `id` (string): Unique todo identifier
- `title` (string): Todo title (required)
- `household_id` (string): Parent household
- `subject_id` (string): Associated subject
- `description` (string): Detailed description (optional)
- `checklist` (list[string]): List of subtasks (optional)
- `difficulty` (DifficultyEnum): Task difficulty level
- `status` (ToDoStatusEnum): Current status
- `date_due` (date): Due date (optional)
- `date_created` (datetime): Creation timestamp
- `date_modified` (datetime): Last modification timestamp

**Business Rules:**

- Soft deletion via status field
- Sortable by due date or modification date
- Checklist supports granular task breakdown

### Habit

Definition of a habit (build or quit).

**Fields:**

- `id` (string): Unique habit identifier
- `title` (string): Habit title (required)
- `household_id` (string): Parent household
- `subject_id` (string): Associated subject
- `description` (string): Detailed description (optional)
- `counter` (HabitCounterEnum): Tracking frequency
- `difficulty` (DifficultyEnum): Habit difficulty level
- `type` (HabitTypeEnum): Build or quit habit
- `status` (HabitStatusEnum): Current status
- `date_created` (datetime): Creation timestamp
- `date_modified` (datetime): Last modification timestamp

**Counter Types:**

- **Daily**: Tracks daily occurrences (YYYY-MM-DD)
- **Weekly**: Tracks weekly occurrences (YYYY-Www, ISO week format)
- **Monthly**: Tracks monthly occurrences (YYYY-MM)

**Business Rules:**

- Soft deletion via status field
- Supports both building new habits and quitting existing ones
- Flexible tracking frequencies for different habit types

### HabitEvent

Single log entry for a habit within a time period.

**Fields:**

- `id` (string): Unique event identifier
- `household_id` (string): Parent household
- `subject_id` (string): Associated subject
- `habit_id` (string): Associated habit
- `period_key` (string): Time period identifier
- `status` (HabitEventStatusEnum): Event outcome
- `note` (string): Optional notes about the event
- `date_created` (datetime): Creation timestamp
- `date_modified` (datetime): Last modification timestamp

**Period Key Formats:**

- Daily: `YYYY-MM-DD` (e.g., "2025-01-15")
- Weekly: `YYYY-Www` (e.g., "2025-W03", ISO week)
- Monthly: `YYYY-MM` (e.g., "2025-01")

**Business Rules:**

- One event per habit per period (enforced via DynamoDB conditional write)
- Deterministic keys enable idempotent operations
- Auto-calculated period keys based on habit counter type

## Enumerations

### DifficultyEnum

- `easy`: Simple tasks requiring minimal effort
- `medium`: Moderate tasks requiring some effort
- `hard`: Challenging tasks requiring significant effort
- `trivial`: Very simple tasks requiring almost no effort

### HabitCounterEnum

- `daily`: Track daily occurrences
- `weekly`: Track weekly occurrences
- `monthly`: Track monthly occurrences

### HabitTypeEnum

- `build`: Building a new positive habit
- `quit`: Quitting an existing negative habit

### Status Enumerations

**HabitStatusEnum:**

- `active`: Currently being tracked
- `archived`: Paused but not deleted
- `deleted`: Soft deleted (hidden from UI)

**ToDoStatusEnum:**

- `active`: Not yet completed
- `completed`: Successfully finished
- `deleted`: Soft deleted (hidden from UI)

**HabitEventStatusEnum:**

- `done`: Successfully completed the habit
- `skipped`: Intentionally skipped (not a failure)
- `failed`: Failed to complete the habit

## Data Ownership Hierarchy

All data follows a strict ownership hierarchy:

```
User → Household → Subject → Entity (ToDo/Habit) → SubEntity (HabitEvent)
```

**Security Implications:**

- Users can only access households they're members of
- Subjects must exist within the user's accessible households
- All operations validate the complete ownership chain
- Path parameters are never trusted without validation

## DynamoDB Key Design

### Partition Key (PK) Patterns

- `AUTHUSER#{user_id}`: User profile data
- `HOUSEHOLD#{household_id}`: All household-scoped data

### Sort Key (SK) Patterns

- `META#PROFILE`: User profile metadata
- `META#HOUSEHOLD`: Household metadata
- `MEMBER#{user_id}`: Household membership
- `SUBJECT#{subject_id}`: Subject information
- `SUBJECT#{subject_id}#TODO#{todo_id}`: Todo items
- `SUBJECT#{subject_id}#HABIT#{habit_id}`: Habit definitions
- `SUBJECT#{subject_id}#HABIT#{habit_id}#EVENT#{period_key}`: Habit events

**Benefits:**

- Efficient queries for related data
- Natural data locality
- Prevents hot partitions
- Supports hierarchical access patterns
