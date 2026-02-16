"""
Lambda handler for updating a household.
"""

from typing import Any, Dict

from controllers.household_controller import HouseholdController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class UpdateHouseholdHandler(BaseHandler):
    """Handler for PUT /households/{householdId}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("update_household", self._update)

    def _update(self):
        item = self.controller.update()
        return success_response(body=item.to_dict())


@lambda_handler_with_errors("update_household")
def lambda_handler(event, context):
    return UpdateHouseholdHandler(event).handler()
