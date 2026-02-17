"""
Lambda handler for habit analytics.
"""

from typing import Dict, Any

from controllers.habit_event_controller import HabitEventController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class GetHabitAnalyticsHandler(BaseHandler):
    """Handler for GET /households/{householdId}/subjects/{subjectId}/habits/{habitId}/analytics"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HabitEventController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("get_habit_analytics", self._get_analytics)

    def _get_analytics(self):
        result = self.controller.get_analytics()
        return success_response(body=result)


@lambda_handler_with_errors("get_habit_analytics")
def lambda_handler(event, context):
    return GetHabitAnalyticsHandler(event).handler()
