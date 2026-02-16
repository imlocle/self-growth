# Bug Fix: Lambda Import Error

## Problem

Frontend login was failing with error:

```
[ERROR] Runtime.ImportModuleError: Unable to import module 'handlers.auth.login': No module named 'src'
```

## Root Cause

Two files had incorrect absolute imports using `from src.models.errors import ...`:

- `src/utils/validation.py` (line 8)
- `src/utils/error_handler.py` (line 8)

When Lambda zips are created from the `src/` directory, there is no `src` module in the package, so these imports fail at runtime.

## Fix Applied

Changed imports from:

```python
from src.models.errors import ...
```

To:

```python
from models.errors import ...
```

## Files Modified

1. `src/utils/validation.py`
2. `src/utils/error_handler.py`

## Deployment Steps

### Option 1: Rebuild and deploy all Lambdas (recommended)

```bash
make rebuild-zips ENV=dev
make deploy ENV=dev
```

### Option 2: Deploy only affected Lambdas (faster)

Since validation.py and error_handler.py are used by most handlers, you should rebuild all:

```bash
make rebuild-zips ENV=dev
make deploy ENV=dev
```

### Option 3: Deploy just the login Lambda (quickest test)

```bash
make deploy-login ENV=dev
```

## Verification

After deployment, test the login endpoint:

```bash
curl -X POST https://your-api-gateway-url/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "YourPassword123!"
  }'
```

Expected response:

```json
{
  "statusCode": 200,
  "body": {
    "AccessToken": "...",
    "IdToken": "...",
    "RefreshToken": "...",
    "ExpiresIn": 3600,
    "TokenType": "Bearer"
  }
}
```

## Prevention

To prevent this in the future:

1. All imports within the `src/` directory should use relative imports (no `src.` prefix)
2. Consider adding a pre-commit hook or linter rule to catch this pattern
3. Add integration tests that actually invoke Lambda handlers

## Related Files

These utilities are imported by many handlers, so all Lambdas are affected:

- All auth handlers (login, signup, confirm-signup)
- All CRUD handlers (todos, habits, blogs, etc.)
- Any handler that uses validation or error handling
