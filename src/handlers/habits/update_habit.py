from controllers.habit_controller import HabitController
from models.errors import NotFoundError
from utils.response_util import error_response, success_response


class UpdateHabitHandler:
    def __init__(self, event):
        self.controller = HabitController(event)

    def handler(self):
        try:
            item = self.controller.update()
            return success_response(body=item.to_dict())
        except NotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response()


def lambda_handler(event, context):
    return UpdateHabitHandler(event).handler()
