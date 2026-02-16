"""
Lambda handler for getting a single household.
"""

from typing import Any, Dict

from controllers.household_controller import HouseholdController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class GetHouseholdHandler(BaseHandler):
    """Handler for GET /households/{householdId}"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("get_household", self._get)

    def _get(self):
        item = self.controller.get()
        return success_response(body=item.to_dict())


@lambda_handler_with_errors("get_household")
def lambda_handler(event, context):
    return GetHouseholdHandler(event).handler()
