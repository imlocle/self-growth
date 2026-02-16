"""
Lambda handler for getting a single habit event.
"""

from typing import Any, Dict

from controllers.habit_event_controller import HabitEventController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class GetHabitEventHandler(BaseHandler):
    """Handler for GET /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events/{periodKey}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HabitEventController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("get_habit_event", self._get)

    def _get(self):
        item = self.controller.get()
        return success_response(body=item.to_dict())


@lambda_handler_with_errors("get_habit_event")
def lambda_handler(event, context):
    return GetHabitEventHandler(event).handler()
