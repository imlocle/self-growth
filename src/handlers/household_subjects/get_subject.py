"""
Lambda handler for getting a single subject.
"""

from typing import Any, Dict

from controllers.household_subject_controller import HouseholdSubjectController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class GetSubjectHandler(BaseHandler):
    """Handler for GET /households/{householdId}/subjects/{subjectId}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdSubjectController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("get_subject", self._get)

    def _get(self):
        item = self.controller.get()
        return success_response(body=item.to_dict())


@lambda_handler_with_errors("get_subject")
def lambda_handler(event, context):
    return GetSubjectHandler(event).handler()
