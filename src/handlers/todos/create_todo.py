"""
Lambda handler for creating todos.
"""

from typing import Any, Dict

from controllers.todo_controller import ToDoController
from handlers.base_handler import BaseHandler, lambda_handler_with_errors
from utils.response_util import success_response


class CreateToDoHandler(BaseHandler):
    """Handler for POST /households/{householdId}/subjects/{subjectId}/todos"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        self.controller = ToDoController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("create_todo", self._create_todo)
    
    def _create_todo(self):
        """Create a new todo"""
        item = self.controller.create()
        return success_response(body=item.to_dict(), status_code=201)


@lambda_handler_with_errors("create_todo")
def lambda_handler(event, context):
    return CreateToDoHandler(event).handler()
