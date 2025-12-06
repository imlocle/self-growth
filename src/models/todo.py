from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Dict, Optional

from models.enum import StatusEnum


@dataclass
class ToDo:
    id: str
    title: str
    date_created: str
    date_modified: str
    description: Optional[str] = None
    status: StatusEnum = StatusEnum.NEW

    # ---------- Constructors ----------

    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> ToDo:
        body_str = event.get("body") or "{}"
        body = json.loads(body_str)
        return cls.from_dict(body)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a raw dict into a coherent ToDo *input* dict.
        Does NOT assign id or timestamps — service layer does that.
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

        return {
            "title": title,
            "description": data.get("description"),
            "status": status,
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> ToDo:
        """
        Build a ToDo from a DynamoDB item.
        """
        return cls(
            id=item["id"],
            title=item["title"],
            description=item.get("description"),
            status=StatusEnum(item["status"]),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    # ---------- Output Methods ----------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a JSON-safe dict for API responses.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }

    def to_dynamo(self) -> Dict[str, Any]:
        """
        Convert to a DynamoDB item dict.
        """
        return self.to_dict()
