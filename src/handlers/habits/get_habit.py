from controllers.habit_controller import HabitController
from utils.errors import NotFoundError
from utils.response_util import error_response, success_response


class GetHabitHandler:
    def __init__(self, event):
        self.controller = HabitController(event)

    def handler(self):
        try:
            item = self.controller.get()
            return success_response(body=item.to_dict())
        except NotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response()


def lambda_handler(event, context):
    return GetHabitHandler(event).handler()
