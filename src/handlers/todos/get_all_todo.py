from controllers.todo_controller import ToDoController
from utils.response_util import error_response, success_response


class GetAllToDoHandler:
    def __init__(self, event):
        self.controller = ToDoController(event)

    def handler(self):
        try:
            return success_response(body=self.controller.get_all())
        except Exception as e:
            return error_response()


def lambda_handler(event, context):
    return GetAllToDoHandler(event).handler()
