from datetime import datetime, timezone
import json
import re
from typing import Any, Dict
import uuid


def generate_id() -> str:
    return uuid.uuid4().hex


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def parse_iso(dt_str: str | None):
    if not dt_str:
        return datetime.min
    # assuming timestamps look like "2025-01-01T10:00:00Z"
    if dt_str.endswith("Z"):
        dt_str = dt_str.replace("Z", "+00:00")
    return datetime.fromisoformat(dt_str)


def to_camel_case(s: str) -> str:
    """
    Convert snake_case or kebab-case to camelCase.
    """
    s = re.sub(r"[-_]+", " ", s).title().replace(" ", "")
    return s[0].lower() + s[1:] if s else s


def dict_keys_to_camel_case(obj: Any):
    """
    Recursively convert all dict keys to camelCase.
    Handles:
    - dict
    - list
    - primitives
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = to_camel_case(key)
            new_dict[new_key] = dict_keys_to_camel_case(value)
        return new_dict

    elif isinstance(obj, list):
        return [dict_keys_to_camel_case(item) for item in obj]

    else:
        return obj


def to_snake_case(s: str) -> str:
    """
    Convert camelCase or PascalCase into snake_case.
    Handles transitions like:
    - userId -> user_id
    - UserID -> user_id
    - dateCreated -> date_created
    """
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def dict_keys_to_snake_case(obj: Any):
    """
    Recursively convert dictionary keys from camelCase to snake_case.
    Handles:
    - dict
    - list
    - primitives
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = to_snake_case(key)
            new_dict[new_key] = dict_keys_to_snake_case(value)
        return new_dict

    elif isinstance(obj, list):
        return [dict_keys_to_snake_case(item) for item in obj]

    else:
        return obj


def parse_enum(enum_class: Any, raw_value: str):
    """
    Universal helper to validate and parse enums across the app.

    Args:
        enum_class: The Enum class to validate against.
        raw_value: The incoming value from input (string/int/etc.).

    Returns:
        An enum instance.

    Raises:
        ValueError: If the value is not valid for the given enum.
    """
    try:
        return enum_class(raw_value)
    except ValueError:
        allowed = [e.value for e in enum_class]
        raise ValueError(f"Invalid value: '{raw_value}'. " f"Allowed values: {allowed}")


def parse_request_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = json.loads(event.get("body", "{}"))
    return dict_keys_to_snake_case(body)
