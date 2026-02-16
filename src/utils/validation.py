"""
Validation utilities with enhanced error handling.
"""

import re
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

        username = username.strip()

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

        email = email.strip().lower()

        # Basic email regex - more comprehensive than before
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise InvalidEmailError(email)

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
        value: str, field_name: str, min_length: int = None, max_length: int = None
    ) -> str:
        """Validate string length"""
        if value is None:
            raise MissingRequiredFieldError(field_name)

        value = value.strip()
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
    def validate_date(value: str, field_name: str) -> date:
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
        max_items: int = None,
        item_validator: callable = None,
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

    validated["username"] = validator.validate_string_length(
        username, "username", min_length=1, max_length=100
    )

    # Password - required
    if "password" not in data:
        raise MissingRequiredFieldError("password")

    validated["password"] = validator.validate_string_length(
        data["password"], "password", min_length=1
    )

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

    # Password - required
    if "password" not in data:
        raise MissingRequiredFieldError("password")

    validated["password"] = validator.validate_string_length(
        data["password"], "password", min_length=8
    )

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

    # Confirmation code - required
    if "confirmation_code" not in data:
        raise MissingRequiredFieldError("confirmation_code")

    validated["confirmation_code"] = validator.validate_string_length(
        data["confirmation_code"], "confirmation_code", min_length=4, max_length=10
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



