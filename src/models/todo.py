from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from models.enum import DifficultyEnum, ToDoStatusEnum
from models.base_model import BaseModel


@dataclass
class ToDo(BaseModel):
    """ToDo entity representing a task for a subject"""
    
    id: str
    title: str
    household_id: str
    subject_id: str
    date_created: str
    date_modified: str

    checklist: Optional[List[str]] = None
    entity: str = "ToDo"
    date_due: Optional[str] = None
    description: Optional[str] = None
    difficulty: DifficultyEnum = DifficultyEnum.EASY
    status: ToDoStatusEnum = ToDoStatusEnum.ACTIVE

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "ToDo":
        """
        Convert a DynamoDB item to a ToDo instance.
        """
        return cls(
            id=item["id"],
            household_id=item["household_id"],
            subject_id=item["subject_id"],
            title=item["title"],
            checklist=item.get("checklist"),
            entity=item.get("entity", "ToDo"),
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
        """Convert ToDo to dictionary for API response"""
        return {
            "id": self.id,
            "household_id": self.household_id,
            "subject_id": self.subject_id,
            "entity": self.entity,
            "title": self.title,
            "checklist": self.checklist,
            "description": self.description,
            "difficulty": self.difficulty.value if isinstance(self.difficulty, DifficultyEnum) else self.difficulty,
            "status": self.status.value if isinstance(self.status, ToDoStatusEnum) else self.status,
            "date_due": self.date_due,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }
