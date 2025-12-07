from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Dict, Optional

from models.enum import BlogStatusEnum


@dataclass
class BlogPost:
    id: str
    title: str
    content: str
    date_created: str
    date_modified: str
    summary: Optional[str] = None
    status: BlogStatusEnum = BlogStatusEnum.DRAFT

    # ---------- Input Helpers ----------

    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate a blog post from an API Gateway event.
        Returns a dict of fields (no id/timestamps).
        """
        body_str = event.get("body") or "{}"
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            raise ValueError("Request body must be valid JSON")

        return cls.from_dict(body)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate incoming blog data and return normalized fields.
        Service layer is responsible for assigning id + timestamps.
        """
        # --- Title ---
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title is required and must be a non-empty string")

        # --- Content ---
        content = data.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content is required and must be a non-empty string")

        # --- Summary (optional) ---
        summary = data.get("summary")
        if summary is not None and not isinstance(summary, str):
            raise ValueError("summary must be a string if provided")

        # --- Status ---
        status_raw = data.get("status", BlogStatusEnum.DRAFT.value)
        try:
            status = BlogStatusEnum(status_raw)
        except ValueError:
            raise ValueError(
                f"Invalid status: '{status_raw}'. "
                f"Expected one of: {[s.value for s in BlogStatusEnum]}"
            )

        return {
            "title": title.strip(),
            "content": content.strip(),
            "summary": summary.strip() if isinstance(summary, str) else None,
            "status": status,
        }

    @classmethod
    def from_json(cls, json_str: str) -> Dict[str, Any]:
        """
        Parse raw JSON string and validate blog data.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Input must be valid JSON")
        return cls.from_dict(data)

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "BlogPost":
        """
        Build a BlogPost from a DynamoDB item.
        """
        return cls(
            id=item["id"],
            title=item["title"],
            content=item["content"],
            summary=item.get("summary"),
            status=BlogStatusEnum(item["status"]),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    # ---------- Output Helpers ----------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to JSON-safe dict for API responses.
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "status": self.status.value,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }

    def to_dynamo(self) -> Dict[str, Any]:
        """
        Convert to a DynamoDB-storable dict.
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "status": self.status.value,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }
