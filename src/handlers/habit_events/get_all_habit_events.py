"""
Lambda handler for listing habit events.
"""

from typing import Any, Dict

from controllers.habit_event_controller import HabitEventController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class GetAllHabitEventsHandler(BaseHandler):
    """Handler for GET /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HabitEventController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("get_all_habit_events", self._get_all)

    def _get_all(self):
        result = self.controller.get_all()
        return success_response(body=result)


@lambda_handler_with_errors("get_all_habit_events")
def lambda_handler(event, context):
    return GetAllHabitEventsHandler(event).handler()
