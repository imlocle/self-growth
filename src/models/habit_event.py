from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from models.base_model import BaseModel
from models.enum import HabitEventStatusEnum
from utils.helper import parse_enum


@dataclass
class HabitEvent(BaseModel):
    id: str
    household_id: str
    subject_id: str
    habit_id: str
    period_key: str
    date_created: str
    date_modified: str

    entity: str = "HabitEvent"
    status: HabitEventStatusEnum = HabitEventStatusEnum.DONE
    note: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates *input* for creating/updating an event.
        Service assigns ids + timestamps + household/subject/habit/period_key.
        """
        status = parse_enum(
            HabitEventStatusEnum,
            data.get("status", HabitEventStatusEnum.DONE.value),
        )
        note = data.get("note")
        return {"status": status, "note": note}

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "HabitEvent":
        return cls(
            id=item["id"],
            household_id=item["household_id"],
            subject_id=item["subject_id"],
            entity=item.get("entity", "HabitEvent"),
            habit_id=item["habit_id"],
            period_key=item["period_key"],
            status=HabitEventStatusEnum(item["status"]),
            note=item.get("note"),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity": self.entity,
            "household_id": self.household_id,
            "subject_id": self.subject_id,
            "habit_id": self.habit_id,
            "period_key": self.period_key,
            "status": self.status.value,
            "note": self.note,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }

    def to_dynamo(self) -> Dict[str, Any]:
        return self.to_dict()
