"""
Lambda handler for deleting a household.
"""

from typing import Any, Dict

from controllers.household_controller import HouseholdController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class DeleteHouseholdHandler(BaseHandler):
    """Handler for DELETE /households/{householdId}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("delete_household", self._delete)

    def _delete(self):
        self.controller.delete()
        return success_response(body={}, status_code=204)


@lambda_handler_with_errors("delete_household")
def lambda_handler(event, context):
    return DeleteHouseholdHandler(event).handler()
