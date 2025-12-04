from dataclasses import dataclass
import json
from typing import Any, Dict, Optional

from src.models.enum import StatusEnum

@dataclass
class ToDo:
    title: str
    description: Optional[str]
    status: StatusEnum = StatusEnum.NEW

    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> "ToDo":
        """
        Build a ToDo from an API Gateway event.
        """
        body_str = event.get("body", "{}")
        body = json.loads(body_str)
        return cls.from_dict(body)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToDo":
        """
        Build a ToDo from a plain dict.
        """
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title is required and must be a non-empty string")

        # Handle status
        status_raw = data.get("status", StatusEnum.NEW.value)
        try:
            status = StatusEnum(status_raw)
        except ValueError:
            raise ValueError(
                f"Invalid status: '{status_raw}'. "
                f"Expected one of: {[s.value for s in StatusEnum]}"
            )

        return cls(
            title=title,
            description=data.get("description"),
            status=status,
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "ToDo":
        """
        Build a ToDo from a JSON string.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "ToDo":
        """
        Build a ToDo from a DynamoDB item.
        """
        return cls(
            title=item["title"],
            description=item.get("description"),
            status=StatusEnum(item["status"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a JSON-serializable dict.
        """
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
        }

    def to_dynamo(self) -> Dict[str, Any]:
        """
        Convert to DynamoDB format.
        """
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
        }