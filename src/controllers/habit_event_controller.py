from typing import Any, Dict

from controllers.base_controller import BaseController
from models.habit_event import HabitEvent
from services.habit_event_service import HabitEventService


class HabitEventController(BaseController):
    def __init__(
        self,
        event: Dict[str, Any],
        habit_event_service: HabitEventService | None = None,
    ):
        super().__init__(event=event, require_auth=True)
        self.habit_event_service = habit_event_service or HabitEventService()
        self.habit_id = self._get_habit_id()

    def _get_habit_id(self) -> str:
        path = self.event.get("pathParameters") or {}
        habit_id = path.get("habitId")
        if not habit_id:
            raise ValueError("Missing habitId in path")
        return habit_id

    def create(self) -> HabitEvent:
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        data = HabitEvent.from_dict(self.body)  # status/note validation only
        return self.habit_event_service.create(
            user_id=self.auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=self.habit_id,
            data=data,
        )
