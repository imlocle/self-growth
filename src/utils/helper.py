from datetime import datetime, timezone
import re
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


def to_camel_case(s: str) -> str:
    """
    Convert snake_case or kebab-case to camelCase.
    """
    s = re.sub(r"[-_]+", " ", s).title().replace(" ", "")
    return s[0].lower() + s[1:] if s else s


def dict_keys_to_camel_case(obj):
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


def dict_keys_to_snake_case(obj):
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
