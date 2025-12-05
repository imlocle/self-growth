from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
from models.enum import VisibilityEnum


@dataclass
class BlogPost:
    id: str
    user_id: str
    title: str
    content: str
    visibility: VisibilityEnum
    date_created: datetime
    date_modified: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlogPost":
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            title=data["title"],
            content=data["content"],
            visibility=VisibilityEnum(data.get("visibility", "private")),
            date_created=datetime.fromisoformat(data["date_created"]),
            date_modified=datetime.fromisoformat(data["date_modified"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "visibility": self.visibility.value,
            "date_created": self.date_created.isoformat(),
            "date_modified": self.date_modified.isoformat(),
        }
