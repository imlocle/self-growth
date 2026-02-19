"""
Validation utilities with enhanced error handling and input sanitization.
"""

import re
import html
from typing import Any, List, Dict, Optional
from datetime import datetime, date
from models.errors import (
    ValidationError,
    InvalidUsernameError,
    InvalidEmailError,
    InvalidPhoneError,
    InvalidEnumError,
    MissingRequiredFieldError,
)


# =========================================================================
# Input Sanitization Functions
# =========================================================================

def sanitize_html(value: str) -> str:
    """
    Sanitize HTML and script content from input strings.
    
    - Strips HTML tags
    - Escapes special characters to prevent XSS
    - Removes script/style content
    
    Args:
        value: Input string to sanitize
        
    Returns:
        Sanitized string safe for storage and display
    """
    if not value:
        return value
    
    # Remove script and style tags with their content
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r'<style[^>]*>.*?</style>', '', value, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove HTML tags
    value = re.sub(r'<[^>]+>', '', value)
    
    # Escape HTML special characters
    value = html.escape(value)
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    return value


def sanitize_string(value: str, allow_newlines: bool = True) -> str:
    """
    Sanitize general string input.
    
    - Strips leading/trailing whitespace
    - Removes HTML/script content
    - Optionally removes newlines
    - Normalizes whitespace
    
    Args:
        value: Input string to sanitize
        allow_newlines: If False, replaces newlines with spaces
        
    Returns:
        Sanitized string
    """
    if not value:
        return value
    
    # Strip leading/trailing whitespace
    value = value.strip()
    
    # Sanitize HTML
    value = sanitize_html(value)
    
    # Handle newlines
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')
    
    # Normalize multiple spaces
    value = re.sub(r' +', ' ', value)
    
    return value


class Validator:
    """Enhanced validator with specific error types"""

    @staticmethod
    def validate_required(value: Any, field_name: str) -> Any:
        """Validate that a required field is present and not empty"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise MissingRequiredFieldError(field_name)
        return value

    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username format"""
        if not username:
            raise MissingRequiredFieldError("username")

        # Sanitize input (no HTML allowed in usernames)
        username = sanitize_string(username, allow_newlines=False)

        if not re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
            raise InvalidUsernameError(username)

        # Check for reserved usernames
        reserved = ["admin", "root", "system", "api", "www", "mail", "support"]
        if username.lower() in reserved:
            raise ValidationError(
                f"Username '{username}' is reserved", field="username", value=username
            )

        return username

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        if not email:
            raise MissingRequiredFieldError("email")

        # Sanitize and normalize
        email = sanitize_string(email, allow_newlines=False).lower()

        # Basic email regex - more comprehensive than before
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise InvalidEmailError(email)

        # Enforce maximum length
        if len(email) > 254:  # RFC 5321
            raise ValidationError(
                "Email address is too long (max 254 characters)",
                field="email",
                value=email
            )

        return email

    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate phone number format"""
        if not phone:
            raise MissingRequiredFieldError("phone_number")

        # Remove all non-digit characters except +
        cleaned_phone = re.sub(r"[^\d+]", "", phone)

        # Check format: optional + followed by 10-15 digits
        if not re.match(r"^\+?[1-9]\d{9,14}$", cleaned_phone):
            raise InvalidPhoneError(phone)

        return cleaned_phone

    @staticmethod
    def validate_enum(value: str, field_name: str, valid_values: List[str]) -> str:
        """Validate enum value"""
        if not value:
            raise MissingRequiredFieldError(field_name)

        if value not in valid_values:
            raise InvalidEnumError(field_name, value, valid_values)

        return value

    @staticmethod
    def validate_string_length(
        value: str, field_name: str, min_length: Optional[int] = None, max_length: Optional[int] = None
    ) -> str:
        """Validate string length with sanitization"""
        if value is None:
            raise MissingRequiredFieldError(field_name)

        # Sanitize input (allow newlines for text fields)
        value = sanitize_string(value, allow_newlines=True)
        length = len(value)

        if min_length is not None and length < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters long",
                field=field_name,
                value=value,
                details={"min_length": min_length, "actual_length": length},
            )

        if max_length is not None and length > max_length:
            raise ValidationError(
                f"{field_name} must be no more than {max_length} characters long",
                field=field_name,
                value=value,
                details={"max_length": max_length, "actual_length": length},
            )

        return value

    @staticmethod
    def validate_date(value: str, field_name: str) -> Optional[date]:
        """Validate date format (YYYY-MM-DD)"""
        if not value:
            return None  # Optional field

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(
                f"{field_name} must be in YYYY-MM-DD format",
                field=field_name,
                value=value,
            )

    @staticmethod
    def validate_list(
        value: List[Any],
        field_name: str,
        max_items: Optional[int] = None,
        item_validator: Optional[Any] = None,
    ) -> List[Any]:
        """Validate list field"""
        if value is None:
            return []

        if not isinstance(value, list):
            raise ValidationError(
                f"{field_name} must be a list", field=field_name, value=value
            )

        if max_items is not None and len(value) > max_items:
            raise ValidationError(
                f"{field_name} can have at most {max_items} items",
                field=field_name,
                value=value,
                details={"max_items": max_items, "actual_items": len(value)},
            )

        # Validate each item if validator provided
        if item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_items.append(item_validator(item))
                except ValidationError as e:
                    # Add list index to error context
                    e.details["list_index"] = i
                    e.details["list_field"] = field_name
                    raise e
            return validated_items

        return value


# Specific validation functions for domain objects
def validate_user_profile_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user profile creation/update data"""
    validator = Validator()

    validated = {}

    # Required fields
    if "username" in data:
        validated["username"] = validator.validate_username(data["username"])

    if "email" in data:
        validated["email"] = validator.validate_email(data["email"])

    # Optional fields
    if "first_name" in data:
        validated["first_name"] = validator.validate_string_length(
            data["first_name"], "first_name", min_length=1, max_length=50
        )

    if "last_name" in data:
        validated["last_name"] = validator.validate_string_length(
            data["last_name"], "last_name", min_length=1, max_length=50
        )

    if "phone_number" in data:
        validated["phone_number"] = validator.validate_phone(data["phone_number"])

    return validated


def validate_todo_data(data: Dict[str, Any], is_create: bool = False) -> Dict[str, Any]:
    """
    Validate todo creation/update data.

    Args:
        data: Input data to validate
        is_create: If True, requires title field

    Returns:
        Validated and normalized data dict

    Raises:
        ValidationError: If validation fails
    """
    validator = Validator()
    validated = {}

    # Title - required for create, optional for update
    if "title" in data:
        validated["title"] = validator.validate_string_length(
            data["title"], "title", min_length=1, max_length=200
        )
    elif is_create:
        raise MissingRequiredFieldError("title")

    # Description - optional
    if "description" in data:
        if data["description"]:
            validated["description"] = validator.validate_string_length(
                data["description"], "description", max_length=1000
            )
        else:
            validated["description"] = None

    # Difficulty - optional with default for create
    if "difficulty" in data:
        valid_difficulties = ["easy", "medium", "hard", "trivial"]
        validated["difficulty"] = validator.validate_enum(
            data["difficulty"], "difficulty", valid_difficulties
        )
    elif is_create:
        validated["difficulty"] = "easy"  # Default value

    # Status - optional with default for create
    if "status" in data:
        valid_statuses = ["active", "completed", "deleted"]
        validated["status"] = validator.validate_enum(
            data["status"], "status", valid_statuses
        )
    elif is_create:
        validated["status"] = "active"  # Default value

    # Date due - optional
    if "date_due" in data:
        if data["date_due"]:
            # Validate format but keep as string for storage
            validator.validate_date(data["date_due"], "date_due")
            validated["date_due"] = data["date_due"]
        else:
            validated["date_due"] = None

    # Checklist - optional
    if "checklist" in data:
        if data["checklist"] is not None:
            validated["checklist"] = validator.validate_list(
                data["checklist"],
                "checklist",
                max_items=20,
                item_validator=lambda item: validator.validate_string_length(
                    str(item), "checklist_item", min_length=1, max_length=100
                ),
            )
        else:
            validated["checklist"] = None

    return validated


def validate_habit_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate habit creation/update data"""
    validator = Validator()

    validated = {}

    # Required fields
    if "title" in data:
        validated["title"] = validator.validate_string_length(
            data["title"], "title", min_length=1, max_length=200
        )

    # Optional fields
    if "description" in data:
        if data["description"]:
            validated["description"] = validator.validate_string_length(
                data["description"], "description", max_length=1000
            )
        else:
            validated["description"] = ""

    if "counter" in data:
        valid_counters = ["daily", "weekly", "monthly"]
        validated["counter"] = validator.validate_enum(
            data["counter"], "counter", valid_counters
        )

    if "difficulty" in data:
        valid_difficulties = ["easy", "medium", "hard", "trivial"]
        validated["difficulty"] = validator.validate_enum(
            data["difficulty"], "difficulty", valid_difficulties
        )

    if "type" in data:
        valid_types = ["build", "quit"]
        validated["type"] = validator.validate_enum(data["type"], "type", valid_types)

    if "status" in data:
        valid_statuses = ["active", "archived", "deleted"]
        validated["status"] = validator.validate_enum(
            data["status"], "status", valid_statuses
        )

    return validated


def validate_habit_event_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate habit event creation data"""
    validator = Validator()

    validated = {}

    # Required fields
    if "status" in data:
        valid_statuses = ["done", "skipped", "failed"]
        validated["status"] = validator.validate_enum(
            data["status"], "status", valid_statuses
        )

    # Optional fields
    if "note" in data:
        if data["note"]:
            validated["note"] = validator.validate_string_length(
                data["note"], "note", max_length=500
            )
        else:
            validated["note"] = ""

    return validated


def validate_login_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate login data.

    Args:
        data: Input data to validate

    Returns:
        Validated and normalized data dict

    Raises:
        ValidationError: If validation fails
    """
    validator = Validator()
    validated = {}

    # Username or email - required
    username = data.get("username") or data.get("email")
    if not username:
        raise MissingRequiredFieldError("username or email")

    # Sanitize username/email input
    validated["username"] = sanitize_string(
        validator.validate_string_length(username, "username", min_length=1, max_length=254),
        allow_newlines=False
    )

    # Password - required (no sanitization, preserve exact input)
    if "password" not in data:
        raise MissingRequiredFieldError("password")

    password = data["password"]
    if not password or len(password) < 1:
        raise ValidationError("Password is required", field="password")
    
    if len(password) > 256:  # Reasonable max for passwords
        raise ValidationError(
            "Password is too long (max 256 characters)",
            field="password"
        )

    validated["password"] = password

    return validated


def validate_signup_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate signup data.

    Args:
        data: Input data to validate

    Returns:
        Validated and normalized data dict

    Raises:
        ValidationError: If validation fails
    """
    validator = Validator()
    validated = {}

    # Email - required
    validated["email"] = validator.validate_email(data.get("email", ""))

    # Password - required (no sanitization, preserve exact input)
    if "password" not in data:
        raise MissingRequiredFieldError("password")

    password = data["password"]
    if not password or len(password) < 8:
        raise ValidationError(
            "Password must be at least 8 characters long",
            field="password"
        )
    
    if len(password) > 256:
        raise ValidationError(
            "Password is too long (max 256 characters)",
            field="password"
        )

    validated["password"] = password

    # Phone number - optional
    if "phone_number" in data and data["phone_number"]:
        validated["phone_number"] = validator.validate_phone(data["phone_number"])
    else:
        validated["phone_number"] = None

    # First name - optional
    if "first_name" in data and data["first_name"]:
        validated["first_name"] = validator.validate_string_length(
            data["first_name"], "first_name", min_length=1, max_length=50
        )
    else:
        validated["first_name"] = None

    # Last name - optional
    if "last_name" in data and data["last_name"]:
        validated["last_name"] = validator.validate_string_length(
            data["last_name"], "last_name", min_length=1, max_length=50
        )
    else:
        validated["last_name"] = None

    return validated


def validate_confirm_signup_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate confirm signup data.

    Args:
        data: Input data to validate

    Returns:
        Validated and normalized data dict

    Raises:
        ValidationError: If validation fails
    """
    validator = Validator()
    validated = {}

    # Email - required
    validated["email"] = validator.validate_email(data.get("email", ""))

    # Confirmation code - required (alphanumeric only, no HTML)
    if "confirmation_code" not in data:
        raise MissingRequiredFieldError("confirmation_code")

    code = sanitize_string(data["confirmation_code"], allow_newlines=False)
    validated["confirmation_code"] = validator.validate_string_length(
        code, "confirmation_code", min_length=4, max_length=10
    )

    return validated

def validate_refresh_token_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate refresh token data.

    Args:
        data: Input data to validate

    Returns:
        Validated data dict

    Raises:
        ValidationError: If validation fails
    """
    if not data or "refresh_token" not in data:
        raise MissingRequiredFieldError("refresh_token")

    validator = Validator()
    validated = {}

    validated["refresh_token"] = validator.validate_string_length(
        data["refresh_token"], "refresh_token", min_length=1
    )

    return validated

def validate_household_data(data: Dict[str, Any], is_create: bool = False) -> Dict[str, Any]:
    """Validate household creation/update data."""
    validator = Validator()
    validated = {}

    if "name" in data:
        validated["name"] = validator.validate_string_length(
            data["name"], "name", min_length=1, max_length=100
        )
    elif is_create:
        raise MissingRequiredFieldError("name")

    return validated


def validate_household_member_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate household member creation data."""
    validator = Validator()
    validated = {}

    if "user_id" not in data or not data["user_id"]:
        raise MissingRequiredFieldError("user_id")
    validated["user_id"] = validator.validate_string_length(
        data["user_id"], "user_id", min_length=1
    )

    if "role" not in data or not data["role"]:
        raise MissingRequiredFieldError("role")
    valid_roles = ["owner", "admin", "member"]
    validated["role"] = validator.validate_enum(data["role"], "role", valid_roles)

    return validated


def validate_household_subject_data(data: Dict[str, Any], is_create: bool = False) -> Dict[str, Any]:
    """Validate household subject creation/update data."""
    validator = Validator()
    validated = {}

    if "type" in data:
        valid_types = ["self","child", "adult", "pet"]
        validated["type"] = validator.validate_enum(data["type"], "type", valid_types)
    elif is_create:
        raise MissingRequiredFieldError("type")

    if "display_name" in data and data["display_name"]:
        validated["display_name"] = validator.validate_string_length(
            data["display_name"], "display_name", min_length=1, max_length=50
        )
    elif "display_name" in data:
        validated["display_name"] = None

    if "dob" in data and data["dob"]:
        validator.validate_date(data["dob"], "dob")
        validated["dob"] = data["dob"]
    elif "dob" in data:
        validated["dob"] = None

    return validated





