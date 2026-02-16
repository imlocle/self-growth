"""
Lambda handler for creating a habit event.
"""

from typing import Any, Dict

from controllers.habit_event_controller import HabitEventController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class CreateHabitEventHandler(BaseHandler):
    """Handler for POST /households/{householdId}/subjects/{subjectId}/habits/{habitId}/events"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HabitEventController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("create_habit_event", self._create)

    def _create(self):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)


@lambda_handler_with_errors("create_habit_event")
def lambda_handler(event, context):
    return CreateHabitEventHandler(event).handler()
