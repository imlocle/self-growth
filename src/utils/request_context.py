"""
Shared RequestContext for extracting and managing Lambda event context.
Used by both Handlers (for logging) and Controllers (for business logic).
"""

import json
from typing import Dict, Any, Optional
from models.auth import AuthUser
from utils.error_handler import log_error_with_context
from utils.helper import to_snake_case


class RequestContext:
    """
    Shared context object that extracts and caches all relevant data from Lambda events.

    Used by:
    - BaseHandler: For error logging context
    - BaseController: For request parsing and business logic

    Features:
    - Lazy loading: Data extracted only when accessed
    - Caching: Each property extracted once per request
    - Single source of truth: No duplicate extraction logic
    """

    def __init__(self, event: Dict[str, Any]):
        self.event = event

        # Caches for lazy-loaded properties
        self._claims_cache: Optional[Dict[str, Any]] = None
        self._path_params_cache: Optional[Dict[str, Any]] = None
        self._query_params_cache: Optional[Dict[str, Any]] = None
        self._body_cache: Optional[Dict[str, Any]] = None
        self._auth_user_cache: Optional[AuthUser] = None
        self._logging_context_cache: Optional[Dict[str, Any]] = None

    # =========================================================================
    # Core Properties (Lazy-loaded and cached)
    # =========================================================================

    @property
    def claims(self) -> Dict[str, Any]:
        """JWT claims from the authorizer"""
        if self._claims_cache is None:
            self._claims_cache = (
                self.event.get("requestContext", {})
                .get("authorizer", {})
                .get("jwt", {})
                .get("claims", {})
            ) or {}
        return self._claims_cache

    @property
    def path_params(self) -> Dict[str, Any]:
        """Path parameters (raw, camelCase keys)"""
        if self._path_params_cache is None:
            self._path_params_cache = self.event.get("pathParameters") or {}
        return self._path_params_cache

    @property
    def query_params(self) -> Dict[str, Any]:
        """Query string parameters"""
        if self._query_params_cache is None:
            self._query_params_cache = self.event.get("queryStringParameters") or {}
        return self._query_params_cache

    @property
    def body(self) -> Dict[str, Any]:
        """Parsed request body with snake_case keys"""
        if self._body_cache is None:
            raw_body = self.event.get("body") or "{}"
            try:
                parsed = json.loads(raw_body)
                # Convert keys to snake_case
                self._body_cache = (
                    {to_snake_case(k): v for k, v in parsed.items()}
                    if isinstance(parsed, dict)
                    else {}
                )
            except json.JSONDecodeError:
                self._body_cache = {}
        return self._body_cache

    @property
    def raw_body(self) -> Optional[str]:
        """Raw request body string"""
        return self.event.get("body")

    @property
    def auth_user(self) -> Optional[AuthUser]:
        """Authenticated user from JWT claims"""
        if self._auth_user_cache is None:
            self._auth_user_cache = AuthUser.from_claims(self.claims)
        return self._auth_user_cache

    # =========================================================================
    # Convenience Properties (Derived from core properties)
    # =========================================================================

    @property
    def user_id(self) -> Optional[str]:
        """User ID from JWT claims"""
        return self.auth_user.user_id if self.auth_user else None

    @property
    def email(self) -> Optional[str]:
        """Email from JWT claims"""
        return self.auth_user.email if self.auth_user else None

    @property
    def household_id(self) -> Optional[str]:
        """Household ID from path parameters"""
        return self.path_params.get("householdId")

    @property
    def subject_id(self) -> Optional[str]:
        """Subject ID from path parameters"""
        return self.path_params.get("subjectId")

    @property
    def todo_id(self) -> Optional[str]:
        """Todo ID from path parameters"""
        return self.path_params.get("todoId")

    @property
    def habit_id(self) -> Optional[str]:
        """Habit ID from path parameters"""
        return self.path_params.get("habitId")

    @property
    def request_id(self) -> Optional[str]:
        """AWS request ID"""
        return self.event.get("requestContext", {}).get("requestId")

    @property
    def http_method(self) -> Optional[str]:
        """HTTP method (GET, POST, etc.)"""
        return self.event.get("httpMethod") or self.event.get("requestContext", {}).get(
            "http", {}
        ).get("method")

    @property
    def path(self) -> Optional[str]:
        """Request path"""
        return self.event.get("requestContext", {}).get("path") or self.event.get(
            "rawPath"
        )

    # =========================================================================
    # Logging Context (For error handling)
    # =========================================================================

    @property
    def logging_context(self) -> Dict[str, Any]:
        """
        Context dictionary optimized for logging.
        Includes all relevant request information with snake_case keys.
        """
        if self._logging_context_cache is None:
            context = {
                "user_id": self.user_id,
                "email": self.email,
                "request_id": self.request_id,
                "http_method": self.http_method,
                "path": self.path,
                "household_id": self.household_id,
                "subject_id": self.subject_id,
                "todo_id": self.todo_id,
                "habit_id": self.habit_id,
            }

            # Add query params if present
            if self.query_params:
                context["query_params"] = self.query_params

            # Add body length for POST/PUT
            if self.raw_body:
                context["request_body_length"] = len(self.raw_body)

            # Remove None values
            self._logging_context_cache = {
                k: v for k, v in context.items() if v is not None
            }

        return self._logging_context_cache

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_path_param(self, key: str, required: bool = False) -> Optional[str]:
        """
        Get a path parameter by key (camelCase).

        Args:
            key: Parameter key (e.g., 'householdId')
            required: If True, raises error when missing

        Returns:
            Parameter value or None

        Raises:
            ValueError: If required and missing
        """
        value = self.path_params.get(key)
        if required and not value:
            from models.errors import ValidationError

            raise ValidationError(f"Missing required path parameter: {key}", field=key)
        return value

    def get_query_param(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a query parameter by key with optional default"""
        return self.query_params.get(key, default)

    def get_body_field(self, key: str, default: Any = None) -> Any:
        """Get a field from the parsed body (snake_case key)"""
        return self.body.get(key, default)

    def require_auth(self) -> AuthUser:
        """
        Require authenticated user.

        Returns:
            AuthUser object

        Raises:
            AuthenticationError: If no authenticated user
        """
        if not self.auth_user:
            from models.errors import AuthenticationError

            raise AuthenticationError("Authentication required")
        return self.auth_user

    def require_household_id(self) -> str:
        """
        Require household ID from path parameters.

        Returns:
            Household ID

        Raises:
            ValidationError: If missing
        """
        if not self.household_id:
            from models.errors import ValidationError

            raise ValidationError(
                "Missing required path parameter: householdId", field="householdId"
            )
        return self.household_id

    def require_subject_id(self) -> str:
        """
        Require subject ID from path parameters.

        Returns:
            Subject ID

        Raises:
            ValidationError: If missing
        """
        if not self.subject_id:
            from models.errors import ValidationError

            raise ValidationError(
                "Missing required path parameter: subjectId", field="subjectId"
            )
        return self.subject_id

    def require_todo_id(self) -> str:
        """
        Require todo ID from path parameters.

        Returns:
            Todo ID

        Raises:
            ValidationError: If missing
        """
        if not self.todo_id:
            from models.errors import ValidationError

            raise ValidationError(
                "Missing required path parameter: todoId", field="todoId"
            )
        return self.todo_id

    def require_habit_id(self) -> str:
        """
        Require habit ID from path parameters.

        Returns:
            Habit ID

        Raises:
            ValidationError: If missing
        """
        if not self.habit_id:
            from models.errors import ValidationError

            raise ValidationError(
                "Missing required path parameter: habitId", field="habitId"
            )
        return self.habit_id

    # =========================================================================
    # Error Logging Integration
    # =========================================================================

    def log_error(self, error: Exception, operation: str, **additional_context):
        """
        Log error with full request context.

        Args:
            error: The exception to log
            operation: Name of the operation that failed
            **additional_context: Extra context to include
        """
        context = {**self.logging_context, **additional_context}
        log_error_with_context(error, operation=operation, **context)


# =========================================================================
# Factory Function
# =========================================================================


def create_request_context(event: Dict[str, Any]) -> RequestContext:
    """Factory function to create RequestContext from Lambda event"""
    return RequestContext(event)
