from controllers.user_profile_controller import UserProfileController
from utils.response_util import success_response, error_response
from models.errors import AuthorizationError


class GetUserProfileHandler:
    def __init__(self, event):
        self.controller = UserProfileController(event)

    def handler(self):
        try:
            profile = self.controller.get()
            return success_response(body=profile.to_dict(), status_code=200)
        except AuthorizationError as e:
            return error_response(message=str(e), status_code=401)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response(message=str(e))


def lambda_handler(event, context):
    return GetUserProfileHandler(event).handler()
