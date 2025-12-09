from controllers.todo_controller import ToDoController
from utils.error_util import NotFoundError
from utils.response_util import error_response, success_response


class DeleteToDoHandler:
    def __init__(self, event):
        self.controller = ToDoController(event)

    def handler(self):
        try:
            self.controller.delete()
            return success_response(body={}, status_code=204)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response(message=str(e))


def lambda_handler(event, context):
    return DeleteToDoHandler(event).handler()
