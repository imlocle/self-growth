"""
Lambda handler for removing a member from a household.
"""

from typing import Any, Dict

from controllers.household_member_controller import HouseholdMemberController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class DeleteMemberHandler(BaseHandler):
    """Handler for DELETE /households/{householdId}/members/{userId}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdMemberController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("delete_member", self._delete)

    def _delete(self):
        self.controller.delete()
        return success_response(body={}, status_code=204)


@lambda_handler_with_errors("delete_member")
def lambda_handler(event, context):
    return DeleteMemberHandler(event).handler()
