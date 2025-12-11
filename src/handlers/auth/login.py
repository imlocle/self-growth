from controllers.auth_controller import AuthController
from utils.response_util import success_response, error_response
from utils.errors import AuthError


class LoginHandler:
    def __init__(self, event):
        self.controller = AuthController(event)

    def handler(self):
        try:
            tokens = self.controller.login()
            return success_response(body=tokens, status_code=200)
        except AuthError as e:
            return error_response(message=str(e), status_code=401)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception:
            return error_response()


def lambda_handler(event, context):
    return LoginHandler(event).handler()
