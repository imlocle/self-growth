from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from models.enum import BlogStatusEnum, BlogVisibilityEnum
from models.base_model import BaseModel
from utils.helper import parse_enum


@dataclass
class BlogPost(BaseModel):
    id: str
    title: str
    content: str
    date_created: str
    date_modified: str

    summary: Optional[str] = None
    status: BlogStatusEnum = BlogStatusEnum.DRAFT
    visibility: BlogVisibilityEnum = BlogVisibilityEnum.PUBLIC

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize incoming blog post data.
        Returns a dict with parsed fields.
        Service assigns id + timestamps.
        """

        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title is required and must be a non-empty string")

        content = data.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content is required and must be a non-empty string")

        summary = data.get("summary")
        if summary is not None and not isinstance(summary, str):
            raise ValueError("summary must be a string if provided")

        status: BlogStatusEnum = parse_enum(
            BlogStatusEnum, data.get("status", BlogStatusEnum.DRAFT.value)
        )

        visibility: BlogVisibilityEnum = parse_enum(
            BlogVisibilityEnum, data.get("status", BlogVisibilityEnum.PUBLIC.value)
        )

        return {
            "title": title.strip(),
            "content": content.strip(),
            "summary": summary.strip() if isinstance(summary, str) else None,
            "status": status,
            "visibility": visibility,
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "BlogPost":
        """
        Convert a DynamoDB item to a BlogPost instance.
        """
        return cls(
            id=item["id"],
            title=item["title"],
            content=item["content"],
            summary=item.get("summary"),
            status=BlogStatusEnum(item["status"]),
            visibility=BlogVisibilityEnum(item.get("visibility", "public")),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "status": self.status.value,
            "visibility": self.visibility.value,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }
