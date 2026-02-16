"""
Lambda handler for adding a member to a household.
"""

from typing import Any, Dict

from controllers.household_member_controller import HouseholdMemberController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class CreateMemberHandler(BaseHandler):
    """Handler for POST /households/{householdId}/members"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdMemberController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("create_member", self._create)

    def _create(self):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)


@lambda_handler_with_errors("create_member")
def lambda_handler(event, context):
    return CreateMemberHandler(event).handler()
