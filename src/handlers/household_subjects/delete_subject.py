"""
Lambda handler for deleting a subject.
"""

from typing import Any, Dict

from controllers.household_subject_controller import HouseholdSubjectController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class DeleteSubjectHandler(BaseHandler):
    """Handler for DELETE /households/{householdId}/subjects/{subjectId}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdSubjectController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("delete_subject", self._delete)

    def _delete(self):
        self.controller.delete()
        return success_response(body={}, status_code=204)


@lambda_handler_with_errors("delete_subject")
def lambda_handler(event, context):
    return DeleteSubjectHandler(event).handler()
