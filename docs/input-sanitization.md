# Input Sanitization & Security

**Last Updated**: February 16, 2026  
**Status**: Implemented

This document describes the input sanitization and validation security measures implemented in the Self-Growth backend API.

---

## Overview

All user input is sanitized and validated before processing to prevent:

- **XSS (Cross-Site Scripting)** attacks
- **HTML injection** attacks
- **SQL injection** (defense in depth, though DynamoDB is NoSQL)
- **Null byte injection**
- **Excessive input lengths** (DoS prevention)

---

## Sanitization Functions

### `sanitize_html(value: str) -> str`

Removes HTML and script content from input strings.

**Operations**:

- Strips `<script>` and `<style>` tags with their content
- Removes all HTML tags
- Escapes HTML special characters (`<`, `>`, `&`, `"`, `'`)
- Removes null bytes (`\x00`)

**Example**:

```python
from utils.validation import sanitize_html

# Input with malicious script
input_str = '<script>alert("XSS")</script>Hello <b>World</b>'

# Output: 'Hello World' (HTML escaped)
sanitized = sanitize_html(input_str)
```

---

### `sanitize_string(value: str, allow_newlines: bool = True) -> str`

General string sanitization with whitespace normalization.

**Operations**:

- Strips leading/trailing whitespace
- Calls `sanitize_html()` to remove HTML/scripts
- Optionally removes newlines (for single-line fields)
- Normalizes multiple spaces to single space

**Example**:

```python
from utils.validation import sanitize_string

# Multi-line text (descriptions, notes)
text = "  Hello\n\nWorld  <script>bad()</script>  "
sanitized = sanitize_string(text, allow_newlines=True)
# Output: "Hello\n\nWorld" (cleaned, newlines preserved)

# Single-line text (usernames, titles)
username = "  user<b>name</b>  "
sanitized = sanitize_string(username, allow_newlines=False)
# Output: "username" (cleaned, no newlines)
```

---

## Field-Specific Validation

All validation functions in `src/utils/validation.py` automatically sanitize input.

### Username

**Rules**:

- 3-20 characters
- Alphanumeric and underscore only (`[a-zA-Z0-9_]`)
- No HTML or special characters
- Reserved names blocked (admin, root, system, etc.)

**Sanitization**: `sanitize_string()` with `allow_newlines=False`

---

### Email

**Rules**:

- Valid email format (RFC 5321)
- Maximum 254 characters
- Lowercase normalized
- No HTML or special characters

**Sanitization**: `sanitize_string()` with `allow_newlines=False`

---

### Phone Number

**Rules**:

- 10-15 digits
- Optional `+` prefix
- Non-digit characters stripped (except `+`)

**Sanitization**: Regex-based cleaning (`[^\d+]` removed)

---

### Text Fields (Titles, Descriptions, Notes)

**Rules**:

- Minimum/maximum length enforced per field
- HTML tags stripped
- Script content removed
- Newlines preserved (for multi-line fields)

**Sanitization**: `sanitize_string()` with `allow_newlines=True`

**Field Limits**:
| Field | Min Length | Max Length |
|-------|------------|------------|
| Todo Title | 1 | 200 |
| Todo Description | 0 | 1000 |
| Habit Title | 1 | 200 |
| Habit Description | 0 | 1000 |
| Habit Event Note | 0 | 500 |
| Blog Post Title | 1 | 200 |
| Blog Post Content | 0 | 10000 |
| Household Name | 1 | 100 |
| Display Name | 1 | 50 |
| First/Last Name | 1 | 50 |

---

### Passwords

**Rules**:

- Minimum 8 characters (enforced by Cognito)
- Maximum 256 characters
- **No sanitization** (preserve exact input for authentication)

**Security Note**: Passwords are never logged or stored in plaintext. They are sent directly to AWS Cognito for hashing and validation.

---

### Enum Values

**Rules**:

- Must match predefined valid values exactly
- Case-sensitive
- No HTML or special characters

**Examples**:

- Todo Status: `active`, `completed`, `deleted`
- Habit Counter: `daily`, `weekly`, `monthly`
- Habit Type: `build`, `quit`
- Member Role: `owner`, `admin`, `member`

---

## Validation Flow

All input validation follows this pattern:

```
1. Handler receives raw request
   ↓
2. Controller extracts body/params
   ↓
3. Controller calls validation function
   ↓
4. Validation function sanitizes input
   ↓
5. Validation function checks rules
   ↓
6. Controller passes validated data to Service
   ↓
7. Service performs business logic
```

**Key Principle**: Validation happens in controllers only. Services receive pre-validated, sanitized data.

---

## Security Best Practices

### 1. Defense in Depth

Even though DynamoDB is NoSQL (no SQL injection risk), we still sanitize input to prevent:

- XSS attacks when data is displayed in web/mobile apps
- HTML injection in user-generated content
- Null byte attacks
- Buffer overflow attempts

### 2. Whitelist Approach

For structured fields (usernames, enums), we use a whitelist approach:

- Only allow specific characters/values
- Reject anything that doesn't match the pattern

### 3. Length Limits

All text fields have maximum lengths to prevent:

- Denial of Service (DoS) attacks
- Database storage abuse
- Performance degradation

### 4. No Client-Side Trust

Never trust client input. All validation happens server-side, even if the mobile app also validates.

---

## Error Responses

When validation fails, the API returns a `400 Bad Request` with details:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "title must be no more than 200 characters long",
  "details": {
    "field": "title",
    "max_length": 200,
    "actual_length": 250
  }
}
```

**Common Validation Errors**:

- `MISSING_REQUIRED_FIELD` - Required field is missing
- `INVALID_USERNAME_ERROR` - Username format invalid
- `INVALID_EMAIL_ERROR` - Email format invalid
- `INVALID_PHONE_ERROR` - Phone number format invalid
- `INVALID_ENUM_ERROR` - Enum value not in valid list
- `VALIDATION_ERROR` - General validation failure (length, format, etc.)

---

## Testing Sanitization

### Test XSS Prevention

```bash
# Attempt to inject script in todo title
curl -X POST https://api.example.com/households/{id}/subjects/{id}/todos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<script>alert(\"XSS\")</script>Buy groceries",
    "description": "Get <b>milk</b> and eggs"
  }'

# Response: Title and description will be sanitized
{
  "todo_id": "...",
  "title": "Buy groceries",  # Script removed
  "description": "Get milk and eggs"  # HTML tags removed
}
```

### Test Length Limits

```bash
# Attempt to exceed max length
curl -X POST https://api.example.com/households/{id}/subjects/{id}/todos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "'$(python3 -c 'print("A" * 201)')'"
  }'

# Response: 400 Bad Request
{
  "error": "VALIDATION_ERROR",
  "message": "title must be no more than 200 characters long",
  "details": {
    "field": "title",
    "max_length": 200,
    "actual_length": 201
  }
}
```

### Test HTML Injection

```bash
# Attempt HTML injection in habit description
curl -X POST https://api.example.com/households/{id}/subjects/{id}/habits \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Exercise",
    "description": "<img src=x onerror=alert(1)>Daily workout"
  }'

# Response: HTML sanitized
{
  "habit_id": "...",
  "title": "Exercise",
  "description": "Daily workout"  # HTML tag removed
}
```

---

## Future Enhancements

### Profanity Filtering (Optional)

Not currently implemented. Could be added using:

- Simple word list matching
- External API (e.g., WebPurify, CleanSpeak)
- ML-based content moderation

**Implementation Considerations**:

- Performance impact (adds latency)
- False positives (legitimate words blocked)
- Multi-language support
- Cultural sensitivity

**Recommendation**: Implement only if user reports indicate a need. Start with a simple word list for English.

---

### Rate Limiting per Field

Currently, rate limiting is at the API level (50 req/sec). Could add per-field limits:

- Max 10 todos created per minute
- Max 5 habits created per hour
- Max 100 habit events per day

---

### Content Moderation

For user-generated content (blog posts, notes), could add:

- Automated content scanning
- Flagging system for inappropriate content
- Admin review queue

---

## References

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Python html.escape() Documentation](https://docs.python.org/3/library/html.html#html.escape)
- [RFC 5321 - Email Address Format](https://tools.ietf.org/html/rfc5321)

---

## Summary

Input sanitization is now fully implemented across all API endpoints:

✅ HTML/script tag stripping  
✅ XSS prevention via HTML escaping  
✅ Maximum field lengths enforced  
✅ Null byte removal  
✅ Whitespace normalization  
✅ Enum validation  
✅ Comprehensive error messages

All user input is sanitized before storage and safe for display in web/mobile applications.
