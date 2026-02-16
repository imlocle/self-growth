"""
Lambda handler for updating a subject.
"""

from typing import Any, Dict

from controllers.household_subject_controller import HouseholdSubjectController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class UpdateSubjectHandler(BaseHandler):
    """Handler for PUT /households/{householdId}/subjects/{subjectId}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdSubjectController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("update_subject", self._update)

    def _update(self):
        item = self.controller.update()
        return success_response(body=item.to_dict())


@lambda_handler_with_errors("update_subject")
def lambda_handler(event, context):
    return UpdateSubjectHandler(event).handler()
