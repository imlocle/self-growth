"""
Lambda handler for confirming user signup.
"""

from typing import Any, Dict

from controllers.auth_controller import AuthController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class ConfirmSignupHandler(BaseHandler):
    """Handler for POST /auth/confirm"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = AuthController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("confirm_signup", self._confirm_signup)
    
    def _confirm_signup(self):
        """Confirm user signup with verification code"""
        result = self.controller.confirm_signup()
        return success_response(body=result, status_code=200)


@lambda_handler_with_errors("confirm_signup")
def lambda_handler(event, context):
    return ConfirmSignupHandler(event).handler()
