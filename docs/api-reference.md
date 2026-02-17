# API Reference

## Base URL

- **Development**: `https://api-dev.self-growth.com` (example)
- **Production**: `https://api.self-growth.com` (example)

## Authentication

All endpoints except authentication endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

## Response Format

All responses return JSON with camelCase keys. Successful responses include the requested data, while error responses include an error message.

**Success Response:**

```json
{
  "statusCode": 200,
  "body": "{\"id\": \"...\", \"title\": \"...\", \"dateCreated\": \"...\"}"
}
```

**Error Response:**

```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Invalid input\"}"
}
```

## Authentication Endpoints

### POST /auth/signup

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "phone_number": "+11234567890",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**

```json
{
  "userSub": "cognito-user-id",
  "userConfirmed": false,
  "codeDelivery": {
    "deliveryMedium": "EMAIL",
    "destination": "u***@example.com"
  },
  "message": "Signup successful. Please confirm the code sent to your email."
}
```

**Error Codes:**

- `400`: Invalid input (weak password, invalid email)
- `409`: Email already exists

### POST /auth/confirm-signup

Confirm user signup with email verification code.

**Request Body:**

```json
{
  "email": "user@example.com",
  "confirmation_code": "123456"
}
```

**Response (200 OK):**

```json
{
  "message": "Signup confirmed. You can now log in."
}
```

**Error Codes:**

- `400`: Invalid confirmation code
- `404`: User not found

### POST /auth/login

Authenticate user and receive JWT tokens.

**Request Body:**

```json
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**

```json
{
  "accessToken": "eyJhbGciOiJSUzI1NiIs...",
  "idToken": "eyJhbGciOiJSUzI1NiIs...",
  "refreshToken": "eyJjdHkiOiJKV1QiLCJlbmMi...",
  "expiresIn": 86400,
  "tokenType": "Bearer"
}
```

**Error Codes:**

- `401`: Invalid credentials
- `400`: User not confirmed

### POST /auth/refresh

Refresh expired access tokens using a refresh token.

**Request Body:**

```json
{
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMi..."
}
```

**Response (200 OK):**

```json
{
  "accessToken": "eyJhbGciOiJSUzI1NiIs...",
  "idToken": "eyJhbGciOiJSUzI1NiIs...",
  "expiresIn": 86400,
  "tokenType": "Bearer"
}
```

**Error Codes:**

- `400`: Invalid or expired refresh token

## User Profile Endpoints

### POST /user-profile

Create user profile (called after signup confirmation).

**Authentication:** Required

**Request Body:**

```json
{
  "username": "john_doe",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+11234567890"
}
```

**Response (201 Created):**

```json
{
  "id": "cognito-sub",
  "username": "john_doe",
  "email": "user@example.com",
  "householdId": "household-id",
  "subjectId": "subject-id",
  "firstName": "John",
  "lastName": "Doe",
  "phoneNumber": "+11234567890",
  "dateCreated": "2025-01-01T10:00:00Z",
  "dateModified": "2025-01-01T10:00:00Z"
}
```

**Error Codes:**

- `400`: Invalid input
- `409`: Username already exists

### GET /user-profile

Get current user profile.

**Authentication:** Required

**Response (200 OK):**

```json
{
  "id": "cognito-sub",
  "username": "john_doe",
  "email": "user@example.com",
  "householdId": "household-id",
  "subjectId": "subject-id",
  "firstName": "John",
  "lastName": "Doe",
  "phoneNumber": "+11234567890",
  "dateCreated": "2025-01-01T10:00:00Z",
  "dateModified": "2025-01-01T10:00:00Z"
}
```

## ToDo Endpoints

### POST /households/{householdId}/subjects/{subjectId}/todos

Create a new todo for a subject.

**Authentication:** Required
**Authorization:** User must be household member; subject must exist in household

**Path Parameters:**

- `householdId` (string): Household identifier
- `subjectId` (string): Subject identifier

**Request Body:**

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "checklist": ["Milk", "Eggs", "Bread"],
  "difficulty": "easy",
  "status": "active",
  "date_due": "2025-01-15"
}
```

**Response (201 Created):**

```json
{
  "id": "todo-id",
  "title": "Buy groceries",
  "householdId": "household-id",
  "subjectId": "subject-id",
  "description": "Milk, eggs, bread",
  "checklist": ["Milk", "Eggs", "Bread"],
  "difficulty": "easy",
  "status": "active",
  "dateDue": "2025-01-15",
  "dateCreated": "2025-01-01T10:00:00Z",
  "dateModified": "2025-01-01T10:00:00Z"
}
```

### GET /households/{householdId}/subjects/{subjectId}/todos/{todoId}

Get a specific todo.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):** ToDo object (same format as create response)

### GET /households/{householdId}/subjects/{subjectId}/todos

Get all todos for a subject.

**Authentication:** Required
**Authorization:** User must be household member

**Query Parameters:**

- `sortBy` (string, optional): Sort order (`date_due` or `date_modified`, default: `date_modified`)
- `limit` (integer, optional): Items per page (1-100)
- `nextToken` (string, optional): Opaque pagination token from previous response
- `status` (string, optional): Filter by status (`active`, `completed`, `deleted`)

**Response (200 OK):**

```json
{
  "items": [
    {
      "id": "todo-id",
      "title": "Buy groceries"
    }
  ],
  "nextToken": "eyJwayI6Ik..."
}
```

### PUT /households/{householdId}/subjects/{subjectId}/todos/{todoId}

Update an existing todo.

**Authentication:** Required
**Authorization:** User must be household member

**Request Body:** Partial update (any fields from create request)

**Response (200 OK):** Updated ToDo object

### DELETE /households/{householdId}/subjects/{subjectId}/todos/{todoId}

Delete a todo (soft delete).

**Authentication:** Required
**Authorization:** User must be household member

**Response (204 No Content)**

## Habit Endpoints

### POST /households/{householdId}/subjects/{subjectId}/habits

Create a new habit for a subject.

**Authentication:** Required
**Authorization:** User must be household member; subject must exist in household

**Request Body:**

```json
{
  "title": "Morning run",
  "description": "5km run every morning",
  "counter": "daily",
  "difficulty": "medium",
  "type": "build",
  "status": "active"
}
```

**Response (201 Created):**

```json
{
  "id": "habit-id",
  "title": "Morning run",
  "householdId": "household-id",
  "subjectId": "subject-id",
  "description": "5km run every morning",
  "counter": "daily",
  "difficulty": "medium",
  "type": "build",
  "status": "active",
  "dateCreated": "2025-01-01T10:00:00Z",
  "dateModified": "2025-01-01T10:00:00Z"
}
```

### GET /households/{householdId}/subjects/{subjectId}/habits/{habitId}

Get a specific habit.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):** Habit object (same format as create response)

### GET /households/{householdId}/subjects/{subjectId}/habits

Get all habits for a subject.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):**

```json
{
  "items": [
    {
      "id": "habit-id",
      "title": "Morning run"
    }
  ],
  "nextToken": null
}
```

**Query Parameters:**

- `limit` (integer, optional): Items per page (1-100)
- `nextToken` (string, optional): Opaque pagination token from previous response
- `status` (string, optional): Filter by status (`active`, `archived`, `deleted`)

### PUT /households/{householdId}/subjects/{subjectId}/habits/{habitId}

Update an existing habit.

**Authentication:** Required
**Authorization:** User must be household member

**Request Body:** Partial update (any fields from create request)

**Response (200 OK):** Updated Habit object

### DELETE /households/{householdId}/subjects/{subjectId}/habits/{habitId}

Delete a habit (soft delete).

**Authentication:** Required
**Authorization:** User must be household member

**Response (204 No Content)**

## Habit Event Endpoints

### POST /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events

Create a habit event (log habit occurrence).

**Authentication:** Required
**Authorization:** User must be household member; habit must exist

**Request Body:**

```json
{
  "status": "done",
  "note": "Completed 5km run in 30 minutes"
}
```

**Response (201 Created):**

```json
{
  "id": "event-id",
  "householdId": "household-id",
  "subjectId": "subject-id",
  "habitId": "habit-id",
  "periodKey": "2025-01-15",
  "status": "done",
  "note": "Completed 5km run in 30 minutes",
  "dateCreated": "2025-01-15T07:30:00Z",
  "dateModified": "2025-01-15T07:30:00Z"
}
```

**Behavior:**

- Period key is auto-calculated based on habit counter type
- One event per period is enforced (returns 400 if duplicate exists)
- Idempotent by design (same action = same DynamoDB key)

**Error Codes:**

- `400`: Event already exists for this period
- `403`: User not authorized
- `404`: Habit not found

### GET /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events

Get all habit events for a habit.

**Authentication:** Required
**Authorization:** User must be household member

**Query Parameters:**

- `limit` (integer, optional): Items per page (1-100)
- `nextToken` (string, optional): Opaque pagination token from previous response
- `status` (string, optional): Filter by status (`done`, `skipped`, `failed`)

**Response (200 OK):**

```json
{
  "items": [
    {
      "id": "event-id",
      "periodKey": "2025-01-15",
      "status": "done"
    }
  ],
  "nextToken": null
}
```

### GET /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events/{periodKey}

Get a single habit event by period key.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):** HabitEvent object

### GET /households/{householdId}/subjects/{subjectId}/habits/{habitId}/analytics

Get analytics for a habit (computed on-the-fly from events).

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):**

```json
{
  "habitId": "habit-id",
  "counter": "daily",
  "totalEvents": 45,
  "distribution": {
    "done": 38,
    "skipped": 5,
    "failed": 2
  },
  "completionRate": 0.8444,
  "currentStreak": 7,
  "longestStreak": 14,
  "firstEventDate": "2025-11-01T08:00:00Z",
  "lastEventDate": "2026-02-16T07:30:00Z"
}
```

## Household Endpoints

### POST /households

Create a new household.

**Authentication:** Required

**Request Body:**

```json
{
  "name": "Smith Family"
}
```

**Response (201 Created):** Household object

### GET /households/{householdId}

Get household details.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):** Household object

### GET /households

List user's households.

**Authentication:** Required

**Response (200 OK):**

```json
{
  "items": [{ "id": "...", "name": "Smith Family" }]
}
```

### PUT /households/{householdId}

Update household.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):** Updated Household object

### DELETE /households/{householdId}

Delete household.

**Authentication:** Required
**Authorization:** User must be household member

**Response (204 No Content)**

## Household Member Endpoints

### POST /households/{householdId}/members

Add a member to a household.

**Authentication:** Required
**Authorization:** User must be household member

**Request Body:**

```json
{
  "user_id": "cognito-sub-of-new-member",
  "role": "member"
}
```

**Response (201 Created):** HouseholdMember object

### GET /households/{householdId}/members

List household members.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):**

```json
{
  "items": [{ "userId": "...", "role": "owner" }]
}
```

### DELETE /households/{householdId}/members/{userId}

Remove a member from a household.

**Authentication:** Required
**Authorization:** User must be household member

**Response (204 No Content)**

## Household Subject Endpoints

### POST /households/{householdId}/subjects

Create a subject in a household.

**Authentication:** Required
**Authorization:** User must be household member

**Request Body:**

```json
{
  "display_name": "John",
  "type": "self",
  "dob": "1990-01-15"
}
```

**Response (201 Created):** HouseholdSubject object

### GET /households/{householdId}/subjects/{subjectId}

Get subject details.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):** HouseholdSubject object

### GET /households/{householdId}/subjects

List all subjects in a household.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):**

```json
{
  "items": [{ "id": "...", "displayName": "John" }]
}
```

### PUT /households/{householdId}/subjects/{subjectId}

Update a subject.

**Authentication:** Required
**Authorization:** User must be household member

**Response (200 OK):** Updated HouseholdSubject object

### DELETE /households/{householdId}/subjects/{subjectId}

Delete a subject.

**Authentication:** Required
**Authorization:** User must be household member

**Response (204 No Content)**

## Blog Post Endpoints

### POST /blogs

Create a new blog post.

**Authentication:** Required

**Request Body:**

```json
{
  "title": "My Reflection",
  "content": "Today I learned...",
  "status": "draft",
  "visibility": "private"
}
```

**Response (201 Created):** BlogPost object

### GET /blogs/{postId}

Get a specific blog post.

**Authentication:** Required

**Response (200 OK):** BlogPost object

### GET /blogs

List user's blog posts.

**Authentication:** Required

**Query Parameters:**

- `limit` (integer, optional): Items per page (1-100)
- `nextToken` (string, optional): Opaque pagination token
- `status` (string, optional): Filter by status (`draft`, `published`, `archived`)

**Response (200 OK):**

```json
{
  "items": [{ "id": "...", "title": "My Reflection" }],
  "nextToken": null
}
```

### PUT /blogs/{postId}

Update a blog post.

**Authentication:** Required

**Response (200 OK):** Updated BlogPost object

## Field Validation

### Common Validations

- **Username**: 3-20 characters, alphanumeric + underscore only
- **Email**: RFC-compliant email format
- **Phone**: 10-15 digits only
- **Difficulty**: Must be one of: `easy`, `medium`, `hard`, `trivial`
- **Dates**: ISO 8601 format (YYYY-MM-DD)

### Habit-Specific Validations

- **Counter**: Must be one of: `daily`, `weekly`, `monthly`
- **Type**: Must be one of: `build`, `quit`
- **Status**: Must be one of: `active`, `archived`, `deleted`

### ToDo-Specific Validations

- **Status**: Must be one of: `active`, `completed`, `deleted`
- **Checklist**: Array of strings (optional)

### Habit Event Validations

- **Status**: Must be one of: `done`, `skipped`, `failed`
- **Period Key**: Auto-generated, cannot be manually set

## Error Codes

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request (validation error)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `409`: Conflict (duplicate resource)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

### Rate Limiting

All endpoints are subject to rate limiting:

- **Burst Limit**: 100 concurrent requests
- **Rate Limit**: 50 requests per second

When rate limited, the API returns `429 Too Many Requests`. Implement exponential backoff retry logic in your client. See [Rate Limiting Documentation](../docs/rate-limiting.md) for details.

### Common Error Messages

- `"Invalid input"`: Request body validation failed
- `"User not authorized"`: User lacks permission for this resource
- `"Resource not found"`: Requested resource doesn't exist
- `"Duplicate resource"`: Resource already exists (e.g., habit event for period)
