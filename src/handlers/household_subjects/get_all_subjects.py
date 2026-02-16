"""
Lambda handler for listing household subjects.
"""

from typing import Any, Dict

from controllers.household_subject_controller import HouseholdSubjectController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class GetAllSubjectsHandler(BaseHandler):
    """Handler for GET /households/{householdId}/subjects"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdSubjectController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("get_all_subjects", self._get_all)

    def _get_all(self):
        result = self.controller.get_all()
        return success_response(body=result)


@lambda_handler_with_errors("get_all_subjects")
def lambda_handler(event, context):
    return GetAllSubjectsHandler(event).handler()
