from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Optional, Dict, Any

from models.enum import HabitDifficultyEnum, HabitTypeEnum, HabitStatusEnum


@dataclass
class Habit:
    id: str
    title: str
    date_created: str
    date_modified: str
    description: Optional[str] = None
    difficulty: HabitDifficultyEnum = HabitDifficultyEnum.EASY
    status: HabitStatusEnum = HabitStatusEnum.ACTIVE
    type: HabitTypeEnum = HabitTypeEnum.BUILD

    # ---------- Input helpers ----------

    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        body_str = event.get("body", "{}")
        body = json.loads(body_str)
        return cls.from_dict(body)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize incoming habit data.
        Does NOT assign id or timestamps - that's service responsibility.
        Returns a dict with parsed fields.
        """
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title is required and must be a non-empty string")

        description = data.get("description")

        type_raw = data.get("type", HabitTypeEnum.BUILD.value)
        try:
            habit_type = HabitTypeEnum(type_raw)
        except ValueError:
            raise ValueError(
                f"Invalid habit type: '{type_raw}'. "
                f"Expected one of: {[t.value for t in HabitTypeEnum]}"
            )

        status_raw = data.get("status", HabitStatusEnum.ACTIVE.value)
        try:
            status = HabitStatusEnum(status_raw)
        except ValueError:
            raise ValueError(
                f"Invalid habit status: '{status_raw}'. "
                f"Expected one of: {[s.value for s in HabitStatusEnum]}"
            )

        difficulty_raw = data.get("difficulty", HabitDifficultyEnum.EASY.value)
        try:
            difficulty = HabitDifficultyEnum(difficulty_raw)
        except ValueError:
            raise ValueError(
                f"Invalid habit difficulty: '{difficulty_raw}'. "
                f"Expected one of: {[s.value for s in HabitDifficultyEnum]}"
            )

        return {
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "type": habit_type,
            "status": status,
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "Habit":
        return cls(
            id=item["id"],
            title=item["title"],
            description=item.get("description"),
            difficulty=HabitDifficultyEnum(item.get("difficulty", "easy")),
            type=HabitTypeEnum(item["type"]),
            status=HabitStatusEnum(item["status"]),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    # ---------- Output helpers ----------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty.value,
            "type": self.type.value,
            "status": self.status.value,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }

    def to_dynamo(self) -> Dict[str, Any]:
        return self.to_dict()
