from typing import Any, Dict

from models.enum import HabitStatusEnum, HabitTypeEnum
from models.habit import Habit
from repositories.habit_repository import HabitRepository
from services.access_service import AccessService
from utils.errors import NotFoundError
from utils.helper import generate_id, parse_enum, utc_now_iso, validate_dict_str_value


class HabitService:
    def __init__(
        self,
        habit_repo: HabitRepository = None,
        access_service: AccessService | None = None,
    ):
        self.habit_repo = habit_repo or HabitRepository()
        self.access = access_service or AccessService()

    def create(
        self, user_id: str, household_id: str, subject_id: str, data: dict
    ) -> Habit:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        self.access.assert_subject_in_household(
            household_id=household_id, subject_id=subject_id
        )
        now = utc_now_iso()
        habit = Habit(
            id=generate_id(),
            household_id=household_id,
            subject_id=subject_id,
            date_created=now,
            date_modified=now,
            **data
        )

        self.habit_repo.create(habit)
        return habit

    def get(
        self, user_id: str, household_id: str, subject_id: str, habit_id: str
    ) -> Habit:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        self.access.assert_subject_in_household(
            household_id=household_id, subject_id=subject_id
        )

        item = self.habit_repo.get(
            household_id=household_id, subject_id=subject_id, habit_id=habit_id
        )
        if not item:
            raise NotFoundError("Not Found")
        return Habit.from_dynamo(item)

    def get_all(
        self,
        user_id: str,
        household_id: str,
        subject_id: str,
        sort_by: str = "date_modifed",
    ) -> Dict[str, Any]:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        self.access.assert_subject_in_household(
            household_id=household_id, subject_id=subject_id
        )

        response = self.habit_repo.get_all(
            household_id=household_id, subject_id=subject_id
        )
        return {
            "items": [Habit.from_dynamo(i) for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey"),
        }

    def update(
        self,
        user_id: str,
        household_id: str,
        subject_id: str,
        habit_id: str,
        data: dict,
    ) -> Habit:
        habit = self.get(
            user_id=user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
        )

        habit.title = validate_dict_str_value(data, "title", habit.title)
        habit.description = data.get("description", habit.description)

        if "type" in data:
            habit.type = parse_enum(HabitTypeEnum, data["type"])

        if "status" in data:
            habit.status = parse_enum(HabitStatusEnum, data["status"])

        self.habit_repo.update(habit=habit)
        return habit

    def delete(
        self, user_id: str, household_id: str, subject_id: str, habit_id: str
    ) -> None:
        habit = self.get(
            user_id=user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
        )
        habit.status = HabitStatusEnum.DELETED
        self.habit_repo.update(user_id=user_id, habit=habit)
