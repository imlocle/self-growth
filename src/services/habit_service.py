from typing import Any, Dict

from models.enum import HabitStatusEnum, HabitTypeEnum
from models.habit import Habit
from repositories.habit_repository import HabitRepository
from utils.error_util import NotFoundError
from utils.helper import generate_id, parse_enum, utc_now_iso


class HabitService:
    def __init__(self, habit_repo: HabitRepository = None):
        self.habit_repo = habit_repo or HabitRepository()

    def create(self, user_id: str, data: dict) -> Habit:
        timestamp = utc_now_iso()

        habit = Habit(
            id=generate_id(), date_created=timestamp, date_modified=timestamp, **data
        )
        self.habit_repo.create(user_id, habit)

        return habit

    def get(self, user_id: str, habit_id: str) -> Habit:
        item = self.habit_repo.get(user_id, habit_id)
        if not item:
            raise NotFoundError("Not Found")
        return Habit.from_dynamo(item)

    def get_all(self, user_id: str) -> Dict[str, Any]:
        response = self.habit_repo.get_all(user_id)
        return {
            "items": [Habit.from_dynamo(i) for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey"),
        }

    def update(self, user_id: str, habit_id: str, data: dict) -> Habit:
        habit = self.get(user_id=user_id, habit_id=habit_id)

        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("title must be a non-empty string")
        else:
            title = habit.title

        description = data.get("description", habit.description)

        if "type" in data:
            habit_type = parse_enum(HabitTypeEnum, data["type"])
        else:
            habit_type = habit.type

        if "status" in data:
            status = parse_enum(HabitStatusEnum, data["status"])
        else:
            status = habit.status

        habit.title = title
        habit.description = description
        habit.type = habit_type
        habit.status = status
        habit.date_modified = utc_now_iso()

        self.habit_repo.update(user_id=user_id, habit=habit)
        return habit

    def delete(self, user_id: str, habit_id: str) -> None:
        habit = self.get(user_id=user_id, habit_id=habit_id)
        habit.status = HabitStatusEnum.DELETED
        habit.date_modified = utc_now_iso()

        self.habit_repo.update(user_id=user_id, habit=habit)
