"""
Lambda handler for token refresh.
"""

from typing import Any, Dict

from controllers.auth_controller import AuthController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class RefreshTokenHandler(BaseHandler):
    """Handler for POST /auth/refresh"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = AuthController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("refresh_token", self._refresh_token)
    
    def _refresh_token(self):
        """Refresh authentication tokens"""
        tokens = self.controller.refresh_token()
        return success_response(body=tokens, status_code=200)


@lambda_handler_with_errors("refresh_token")
def lambda_handler(event, context):
    return RefreshTokenHandler(event).handler()
