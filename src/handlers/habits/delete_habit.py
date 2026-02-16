"""
Lambda handler for deleting a habit.
"""

from typing import Dict, Any

from controllers.habit_controller import HabitController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class DeleteHabitHandler(BaseHandler):
    """Handler for DELETE /households/{householdId}/subjects/{subjectId}/habits/{habitId}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HabitController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("delete_habit", self._delete)

    def _delete(self):
        self.controller.delete()
        return success_response(body={}, status_code=204)


@lambda_handler_with_errors("delete_habit")
def lambda_handler(event, context):
    return DeleteHabitHandler(event).handler()
