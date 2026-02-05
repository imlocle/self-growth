from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from models.base_model import BaseModel
from models.enum import (
    HabitCounterEnum,
    DifficultyEnum,
    HabitTypeEnum,
    HabitStatusEnum,
)
from utils.helper import parse_enum


@dataclass
class Habit(BaseModel):
    id: str
    title: str
    household_id: str
    subject_id: str
    date_created: str
    date_modified: str

    counter: HabitCounterEnum = HabitCounterEnum.DAILY
    entity: str = "Habit"
    description: Optional[str] = None
    difficulty: DifficultyEnum = DifficultyEnum.EASY
    status: HabitStatusEnum = HabitStatusEnum.ACTIVE
    type: HabitTypeEnum = HabitTypeEnum.BUILD

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize incoming habit data.
        Returns a dict with parsed fields.
        Service assigns id + timestamps.
        """

        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title is required and must be a non-empty string")

        counter: HabitCounterEnum = parse_enum(
            HabitCounterEnum, data.get("counter", HabitCounterEnum.DAILY.value)
        )

        description = data.get("description")

        difficulty: DifficultyEnum = parse_enum(
            DifficultyEnum, data.get("difficulty", DifficultyEnum.EASY.value)
        )
        habit_type: HabitTypeEnum = parse_enum(
            HabitTypeEnum, data.get("type", HabitTypeEnum.BUILD.value)
        )
        status: HabitStatusEnum = parse_enum(
            HabitStatusEnum, data.get("status", HabitStatusEnum.ACTIVE.value)
        )

        return {
            "title": title.strip(),
            "counter": counter,
            "description": description,
            "difficulty": difficulty,
            "type": habit_type,
            "status": status,
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "Habit":
        """
        Convert a DynamoDB item to a Habit instance.
        """
        return cls(
            id=item["id"],
            household_id=item["household_id"],
            subject_id=item["subject_id"],
            title=item["title"],
            description=item.get("description"),
            counter=HabitCounterEnum(item.get("counter", HabitCounterEnum.DAILY.value)),
            difficulty=DifficultyEnum(
                item.get("difficulty", DifficultyEnum.EASY.value)
            ),
            entity=item.get("entity", "Habit"),
            type=HabitTypeEnum(item["type"]),
            status=HabitStatusEnum(item["status"]),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity": self.entity,
            "household_id": self.household_id,
            "subject_id": self.subject_id,
            "title": self.title,
            "description": self.description,
            "counter": self.counter.value,
            "difficulty": self.difficulty.value,
            "status": self.status.value,
            "type": self.type.value,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }
