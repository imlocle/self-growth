"""
Lambda handler for getting all todos.
"""

from typing import Dict, Any

from controllers.todo_controller import ToDoController
from utils.response_util import success_response
from handlers.base_handler import BaseHandler, lambda_handler_with_errors


class GetAllToDoHandler(BaseHandler):
    """Handler for GET /households/{householdId}/subjects/{subjectId}/todos"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        # Share RequestContext with Controller
        self.controller = ToDoController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("get_all_todos", self._get_all_todos)
    
    def _get_all_todos(self):
        """Get all todos for a subject"""
        result = self.controller.get_all()
        return success_response(body=result)


@lambda_handler_with_errors("get_all_todos")
def lambda_handler(event, context):
    return GetAllToDoHandler(event).handler()
