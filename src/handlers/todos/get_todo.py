"""
Lambda handler for getting a single todo.
"""

from typing import Dict, Any

from controllers.todo_controller import ToDoController
from utils.response_util import success_response
from handlers.base_handler import BaseHandler, lambda_handler_with_errors


class GetToDoHandler(BaseHandler):
    """Handler for GET /households/{householdId}/subjects/{subjectId}/todos/{todoId}"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        # Share RequestContext with Controller
        self.controller = ToDoController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("get_todo", self._get_todo)
    
    def _get_todo(self):
        """Get a single todo"""
        item = self.controller.get()
        return success_response(body=item.to_dict())


@lambda_handler_with_errors("get_todo")
def lambda_handler(event, context):
    return GetToDoHandler(event).handler()
