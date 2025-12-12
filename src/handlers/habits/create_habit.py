from controllers.habit_controller import HabitController
from utils.response_util import success_response, error_response


class CreateHabitHandler:
    def __init__(self, event):
        self.controller = HabitController(event)

    def handler(self):
        try:
            item = self.controller.create()
            return success_response(body=item.to_dict(), status_code=201)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response()


def lambda_handler(event, context):
    return CreateHabitHandler(event).handler()
