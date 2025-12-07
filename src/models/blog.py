from dataclasses import dataclass
from typing import Dict, Any

from models.enum import VisibilityEnum


@dataclass
class BlogPost:
    id: str
    title: str
    content: str
    visibility: VisibilityEnum
    date_created: str
    date_modified: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "visibility": self.visibility.value,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }

    def to_dynamo(self) -> Dict[str, Any]:
        return self.to_dict()
