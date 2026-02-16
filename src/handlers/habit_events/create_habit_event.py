from controllers.habit_event_controller import HabitEventController
from utils.response_util import success_response, error_response


class CreateHabitEventHandler:
    def __init__(self, event):
        self.controller = HabitEventController(event)

    def handler(self):
        try:
            item = self.controller.create()
            return success_response(body=item.to_dict(), status_code=201)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response(message=str(e))


def lambda_handler(event, context):
    return CreateHabitEventHandler(event).handler()
