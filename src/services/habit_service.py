from typing import Any, Dict

from models.enum import HabitStatusEnum, HabitTypeEnum
from models.habit import Habit
from repositories.habit_repository import HabitRepository
from utils.helper import generate_id, utc_now_iso


class HabitService:
    def __init__(self, habit_repo: HabitRepository = None):
        self.habit_repo = habit_repo or HabitRepository()

    def create(self, user_id: str, data: dict) -> Habit:
        parsed = Habit.from_dict(data)

        timestamp = utc_now_iso()

        habit = Habit(
            id=generate_id(), date_created=timestamp, date_modified=timestamp, **parsed
        )
        self.habit_repo.create(user_id, habit)
        return habit

    def get(self, user_id: str, habit_id: str) -> Habit:
        item = self.habit_repo.get(user_id, habit_id)
        if not item:
            raise ValueError("Not Found")
        return Habit.from_dynamo(item)

    def get_all(self, user_id: str) -> Dict[str, Any]:
        response = self.habit_repo.get_all(user_id)
        return {
            "items": [Habit.from_dynamo(i) for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey"),
        }

    def update(self, user_id: str, habit_id: str, data: dict) -> Habit:
        existing = self.habit_repo.get(user_id=user_id, habit_id=habit_id)
        if not existing:
            raise ValueError("Not Found")

        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Title must be a non-empty string")
        else:
            title = existing["title"]

        description = data.get("description", existing.get("description"))

        if "type" in data:
            type_raw = data["type"]
            try:
                habit_type = HabitTypeEnum(type_raw)
            except ValueError:
                raise ValueError(
                    f"Invalid status: '{type_raw}'. "
                    f"Expected one of: {[s.value for s in HabitTypeEnum]}"
                )
        else:
            habit_type = existing["type"]

        if "status" in data:
            status_raw = data["status"]
            try:
                status = HabitStatusEnum(status_raw)
            except ValueError:
                raise ValueError(
                    f"Invalid status: '{status_raw}'. "
                    f"Expected one of: {[s.value for s in HabitStatusEnum]}"
                )
        else:
            status = existing["status"]

        updated_habit = Habit(
            id=existing["id"],
            title=title,
            description=description,
            type=habit_type,
            status=status,
            date_created=existing["date_created"],
            date_modified=utc_now_iso(),
        )
        self.habit_repo.update(user_id=user_id, habit=updated_habit)
        return updated_habit
