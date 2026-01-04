from controllers.user_profile_controller import UserProfileController
from utils.errors import AuthError
from utils.response_util import success_response, error_response


class CreateUserProfileHandler:
    def __init__(self, event):
        self.controller = UserProfileController(event)

    def handler(self):
        try:
            profile = self.controller.create()
            return success_response(body=profile.to_dict(), status_code=201)
        except AuthError as e:
            return error_response(message=str(e), status_code=401)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response(message=str(e))


def lambda_handler(event, context):
    return CreateUserProfileHandler(event).handler()
