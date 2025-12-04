from dataclasses import dataclass
import json
from typing import Any, Dict

@dataclass
class User:
    id: str
    first_name: str
    last_name: str
    username: str
    points: int = 0
    level: int = 1

    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> "User":
        """
        Build a ToDo from an API Gateway event.
        """
        body_str = event.get("body", "{}")
        body = json.loads(body_str)
        return cls.from_dict(body)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """
        Build a User from a plain dict.
        """
        # Validate names
        first_name = data.get("first_name")
        if not isinstance(first_name, str) or not first_name.strip():
            raise ValueError("First name is required and must be a non-empty string")

        last_name = data.get("last_name")
        if not isinstance(last_name, str) or not last_name.strip():
            raise ValueError("Last name is required and must be a non-empty string")

        username = data.get("username")
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username is required and must be a non-empty string")

        return cls(
            id=data.get("id"),
            first_name=first_name,
            last_name=last_name,
            username=username,
            points = data.get("points", 0),
            level = data.get("level", 1)
        )

    @classmethod
    def from_json(cls, json_str: str) -> "User":
        """
        Build a User from a JSON string.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "User":
        """
        Build a User from a DynamoDB item.
        """
        return cls(
            id = item.get("id"),
            first_name = item.get("first_name"),
            last_name = item.get("last_name"),
            username = item.get("username"),
            points = item.get("points"),
            level = item.get("level"),
        )