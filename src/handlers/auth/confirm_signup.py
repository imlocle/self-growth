from controllers.auth_controller import AuthController
from utils.response_util import success_response, error_response
from models.errors import AuthorizationError


class ConfirmSignupHandler:
    def __init__(self, event):
        self.controller = AuthController(event)

    def handler(self):
        try:
            result = self.controller.confirm_signup()
            return success_response(body=result, status_code=200)
        except AuthorizationError as e:
            return error_response(message=str(e), status_code=400)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception:
            return error_response()


def lambda_handler(event, context):
    return ConfirmSignupHandler(event).handler()
