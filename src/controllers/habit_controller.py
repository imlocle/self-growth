from typing import Any, Dict

from models.habit import Habit
from services.habit_service import HabitService


class HabitController:
    def __init__(self, event, habit_service: HabitService = None):
        self.event = event
        # Create AuthService to get user_id
        self.user_id = "1"
        self.data = self.validate_data()
        self.habit_service = habit_service or HabitService()

    def validate_data(self) -> Dict[str, Any]:
        return Habit.from_event(self.event)

    def create(self) -> Habit:
        return self.habit_service.create(self.user_id, self.data)

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
        habit_id = self._get_path_params_id()
        return self.habit_service.update(
            user_id=self.user_id, habit_id=habit_id, data=self.data
        )

    def _get_path_params_id(self) -> str:
        return self.event.get("pathParameters", {}).get("habitId")
