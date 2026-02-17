# Security Quick Reference

**For Developers**: Quick guide to input sanitization in the Self-Growth backend.

---

## TL;DR

All user input is automatically sanitized. Just use the validation functions in `src/utils/validation.py` and you're protected against XSS, HTML injection, and length-based attacks.

---

## How It Works

```python
# In your controller
from utils.validation import validate_todo_data

# This automatically sanitizes all fields
validated_data = validate_todo_data(self.body, is_create=True)

# Pass sanitized data to service
self.todo_service.create(user_id=self.user_id, data=validated_data)
```

That's it! No additional sanitization needed.

---

## What Gets Sanitized

### Automatically Sanitized

- HTML tags removed: `<script>`, `<b>`, `<img>`, etc.
- Special characters escaped: `<`, `>`, `&`, `"`, `'`
- Null bytes removed: `\x00`
- Whitespace normalized
- Length limits enforced

### NOT Sanitized

- Passwords (preserved exactly as entered)
- Tokens (preserved exactly as entered)

---

## Available Validation Functions

```python
from utils.validation import (
    validate_todo_data,           # Todos
    validate_habit_data,          # Habits
    validate_habit_event_data,    # Habit events
    validate_user_profile_data,   # User profiles
    validate_household_data,      # Households
    validate_household_member_data,    # Members
    validate_household_subject_data,   # Subjects
    validate_login_data,          # Login
    validate_signup_data,         # Signup
    validate_confirm_signup_data, # Confirmation
    validate_refresh_token_data,  # Token refresh
)
```

---

## Field Length Limits

| Field Type   | Max Length |
| ------------ | ---------- |
| Email        | 254        |
| Password     | 256        |
| Username     | 20         |
| Names        | 50         |
| Titles       | 200        |
| Descriptions | 1000       |
| Notes        | 500        |
| Blog Content | 10000      |

---

## Examples

### Creating a New Entity

```python
# Controller method
def create(self) -> ToDo:
    household_id = self.require_household_id()
    subject_id = self.require_subject_id()

    # Validate and sanitize in one step
    validated_data = validate_todo_data(self.body, is_create=True)

    # Pass to service (already sanitized)
    return self.todo_service.create(
        user_id=self.user_id,
        household_id=household_id,
        subject_id=subject_id,
        data=validated_data,
    )
```

### Updating an Entity

```python
# Controller method
def update(self) -> ToDo:
    household_id = self.require_household_id()
    subject_id = self.require_subject_id()
    todo_id = self.require_todo_id()

    # Validate and sanitize (is_create=False for updates)
    validated_data = validate_todo_data(self.body, is_create=False)

    # Pass to service (already sanitized)
    return self.todo_service.update(
        user_id=self.user_id,
        household_id=household_id,
        subject_id=subject_id,
        todo_id=todo_id,
        data=validated_data,
    )
```

---

## Custom Validation

If you need custom validation for a new field:

```python
from utils.validation import Validator, sanitize_string

validator = Validator()

# For text fields
sanitized_value = validator.validate_string_length(
    value=input_value,
    field_name="my_field",
    min_length=1,
    max_length=100
)

# For single-line fields (no newlines)
sanitized_value = sanitize_string(input_value, allow_newlines=False)

# For multi-line fields (preserve newlines)
sanitized_value = sanitize_string(input_value, allow_newlines=True)
```

---

## Testing Sanitization

```python
# In your test file
from utils.validation import sanitize_html

def test_xss_prevention():
    malicious_input = '<script>alert("XSS")</script>Hello'
    sanitized = sanitize_html(malicious_input)

    assert 'script' not in sanitized.lower()
    assert 'Hello' in sanitized
```

---

## Common Mistakes to Avoid

### ❌ Don't sanitize in services

```python
# BAD - Services should receive pre-sanitized data
def create(self, data: Dict[str, Any]):
    data['title'] = sanitize_html(data['title'])  # ❌ Wrong layer
    # ...
```

### ✅ Do sanitize in controllers

```python
# GOOD - Controllers validate and sanitize
def create(self):
    validated_data = validate_todo_data(self.body, is_create=True)  # ✅ Correct
    return self.service.create(data=validated_data)
```

### ❌ Don't sanitize passwords

```python
# BAD - Passwords should be preserved exactly
validated['password'] = sanitize_string(password)  # ❌ Wrong
```

### ✅ Do preserve passwords

```python
# GOOD - Passwords are validated but not sanitized
if len(password) < 8:
    raise ValidationError("Password too short")
validated['password'] = password  # ✅ Correct
```

---

## Error Handling

Validation errors return 400 with details:

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

---

## Performance

Sanitization is fast:

- Regex operations: < 1ms per field
- No external API calls
- No database lookups
- In-memory processing

---

## Questions?

See full documentation:

- [Input Sanitization Guide](./input-sanitization.md)
- [API Reference](./api-reference.md)
- [Architecture Overview](./architecture-overview.md)

---

## Summary

✅ Use validation functions in controllers  
✅ All text fields are automatically sanitized  
✅ Length limits are enforced  
✅ Passwords are preserved  
✅ No additional work needed

Just validate in controllers, and you're secure!
