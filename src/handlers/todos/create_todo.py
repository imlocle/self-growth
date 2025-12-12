from typing import Any, Dict

from controllers.todo_controller import ToDoController
from utils.errors import AuthError
from utils.response_util import success_response, error_response


class CreateToDoHandler:
    def __init__(self, event: Dict[str, Any]):
        self.controller = ToDoController(event)

    def handler(self):
        try:
            item = self.controller.create()
            return success_response(body=item.to_dict(), status_code=201)
        except AuthError as e:
            return error_response(message=str(e), status_code=401)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response()


def lambda_handler(event, context):
    return CreateToDoHandler(event).handler()
