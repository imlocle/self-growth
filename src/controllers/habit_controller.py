from typing import Any, Dict, Optional

from controllers.base_controller import BaseController
from models.habit import Habit
from services.habit_service import HabitService


class HabitController(BaseController):
    def __init__(self, event: Dict[str, Any], request_context=None, habit_service: HabitService = None):
        super().__init__(event=event, request_context=request_context, require_auth=True)

        self.habit_service = habit_service or HabitService()
        self.habit_id = self._get_habit_id()

    def _get_habit_id(self) -> Optional[str]:
        path = self.event.get("pathParameters") or {}
        return path.get("habitId")

    def create(self) -> Habit:
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        data = Habit.from_dict(self.body)
        return self.habit_service.create(
            user_id=self.auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            data=data,
        )

    def get(self) -> Habit:
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        return self.habit_service.get(
            user_id=self.auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=self.habit_id,
        )

    def get_all(self) -> Dict[str, Any]:
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        pagination = self.get_pagination_params()

        from utils.helper import decode_next_token, encode_next_token
        next_token = decode_next_token(pagination.get("next_token"))

        response = self.habit_service.get_all(
            user_id=self.auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            limit=pagination.get("limit"),
            next_token=next_token,
            status=pagination.get("status"),
        )
        return {
            "items": [i.to_dict() for i in response.get("items")],
            "nextToken": encode_next_token(response.get("lastEvaluatedKey")),
        }

    def update(self) -> Habit:
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        return self.habit_service.update(
            user_id=self.auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=self.habit_id,
            data=self.body,
        )

    def delete(self) -> None:
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        return self.habit_service.delete(
            user_id=self.auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=self.habit_id,
        )
