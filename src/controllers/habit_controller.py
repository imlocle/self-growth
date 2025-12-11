from typing import Any, Dict

from models.habit import Habit
from services.habit_service import HabitService
from utils.helper import parse_request_body


class HabitController:
    def __init__(self, event: Dict[str, Any], habit_service: HabitService = None):
        self.event = event
        # Create AuthService to get user_id
        self.user_id = "1"
        self.habit_service = habit_service or HabitService()

    def create(self) -> Habit:
        body = parse_request_body(self.event)
        data = Habit.from_dict(body)
        return self.habit_service.create(self.user_id, data)

    def get(self) -> Habit:
        habit_id = self._get_path_params_id()
        return self.habit_service.get(self.user_id, habit_id)

    def get_all(self) -> Dict[str, Any]:
        response = self.habit_service.get_all(self.user_id)
        return {
            "items": [i.to_dict() for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey"),
        }

    def update(self) -> Habit:
        data = parse_request_body(self.event)
        habit_id = self._get_path_params_id()
        return self.habit_service.update(
            user_id=self.user_id, habit_id=habit_id, data=data
        )

    def _get_path_params_id(self) -> str:
        return self.event.get("pathParameters", {}).get("habitId")
