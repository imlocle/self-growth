"""
Lambda handler for creating a household.
"""

from typing import Any, Dict

from controllers.household_controller import HouseholdController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class CreateHouseholdHandler(BaseHandler):
    """Handler for POST /households"""

    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = HouseholdController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("create_household", self._create)

    def _create(self):
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)


@lambda_handler_with_errors("create_household")
def lambda_handler(event, context):
    return CreateHouseholdHandler(event).handler()
