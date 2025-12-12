from controllers.user_profile_controller import UserProfileController
from utils.response_util import success_response, error_response
from utils.errors import AuthError


class GetUserProfileHandler:
    def __init__(self, event):
        self.controller = UserProfileController(event)

    def handler(self):
        try:
            profile = self.controller.get()
            return success_response(body=profile.to_dict(), status_code=200)
        except AuthError as e:
            return error_response(message=str(e), status_code=401)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            print(e)
            return error_response()


def lambda_handler(event, context):
    return GetUserProfileHandler(event).handler()
