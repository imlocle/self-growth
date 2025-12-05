from controllers.todo_controller import ToDoController
from utils.response_util import error_response, success_response


class UpdateToDoHandler:
    def __init__(self, event):
        self.controller = ToDoController(event)

    def handler(self):
        try:
            item = self.controller.update()
            if not item:
                return error_response(message="Not Found", status_code=404)
            return success_response(body=item.to_dict())
        except Exception as e:
            return error_response(message=str(e))


def lambda_handler(event, context):
    return UpdateToDoHandler(event).handler()
