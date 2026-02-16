"""
Lambda handler for creating a subject in a household.
"""

from typing import Any, Dict

from controllers.household_subject_controller import HouseholdSubjectController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class CreateSubjectHandler(BaseHandler):
    """Handler for POST /households/{householdId}/subjects"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdSubjectController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("create_subject", self._create)

    def _create(self):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)


@lambda_handler_with_errors("create_subject")
def lambda_handler(event, context):
    return CreateSubjectHandler(event).handler()
