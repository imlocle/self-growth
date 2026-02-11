"""
Lambda handler for user signup.
"""

from typing import Any, Dict

from controllers.auth_controller import AuthController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class SignupHandler(BaseHandler):
    """Handler for POST /auth/signup"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = AuthController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("signup", self._signup)
    
    def _signup(self):
        """Register a new user"""
        result = self.controller.signup()
        return success_response(body=result, status_code=200)


@lambda_handler_with_errors("signup")
def lambda_handler(event, context):
    return SignupHandler(event).handler()
