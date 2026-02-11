"""
Lambda handler for user login.
"""

from typing import Any, Dict

from controllers.auth_controller import AuthController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class LoginHandler(BaseHandler):
    """Handler for POST /auth/login"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = AuthController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("login", self._login)
    
    def _login(self):
        """Authenticate user and return tokens"""
        tokens = self.controller.login()
        return success_response(body=tokens, status_code=200)


@lambda_handler_with_errors("login")
def lambda_handler(event, context):
    return LoginHandler(event).handler()
