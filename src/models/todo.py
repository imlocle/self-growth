from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from models.enum import DifficultyEnum, ToDoStatusEnum
from models.base_model import BaseModel
from utils.helper import parse_enum


@dataclass
class ToDo(BaseModel):
    id: str
    title: str
    date_created: str
    date_modified: str

    checklist: Optional[List[str]] = None
    date_due: Optional[str] = None
    description: Optional[str] = None
    difficulty: DifficultyEnum = DifficultyEnum.EASY
    status: ToDoStatusEnum = ToDoStatusEnum.ACTIVE

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize incoming todo data.
        Returns a dict with parsed fields.
        Service assigns id + timestamps.
        """

        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title is required and must be a non-empty string")

        checklist = data.get("checklist")
        if checklist is not None:
            if not isinstance(checklist, list):
                raise ValueError("checklist must be a list of strings")

            if not all(isinstance(item, str) and item.strip() for item in checklist):
                raise ValueError("checklist must contain only non-empty strings")

        difficulty: DifficultyEnum = parse_enum(
            DifficultyEnum, data.get("difficulty", DifficultyEnum.EASY.value)
        )
        status: ToDoStatusEnum = parse_enum(
            ToDoStatusEnum, data.get("status", ToDoStatusEnum.ACTIVE.value)
        )

        return {
            "title": title.strip(),
            "checklist": checklist,
            "description": data.get("description"),
            "difficulty": difficulty,
            "status": status,
            "date_due": data.get("date_due"),
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "ToDo":
        """
        Convert a DynamoDB item to a ToDo instance.
        """
        return cls(
            id=item["id"],
            title=item["title"],
            checklist=item.get("checklist"),
            description=item.get("description"),
            difficulty=DifficultyEnum(
                item.get("difficulty", DifficultyEnum.EASY.value)
            ),
            status=ToDoStatusEnum(item["status"]),
            date_due=item.get("date_due"),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "checklist": self.checklist,
            "description": self.description,
            "difficulty": self.difficulty.value,
            "status": self.status.value,
            "date_due": self.date_due,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }
