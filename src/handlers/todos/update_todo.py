"""
Lambda handler for updating a todo.
"""

from typing import Dict, Any

from controllers.todo_controller import ToDoController
from utils.response_util import success_response
from handlers.base_handler import BaseHandler, lambda_handler_with_errors


class UpdateToDoHandler(BaseHandler):
    """Handler for PUT /households/{householdId}/subjects/{subjectId}/todos/{todoId}"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        # Share RequestContext with Controller
        self.controller = ToDoController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("update_todo", self._update_todo)
    
    def _update_todo(self):
        """Update an existing todo"""
        item = self.controller.update()
        return success_response(body=item.to_dict())


@lambda_handler_with_errors("update_todo")
def lambda_handler(event, context):
    return UpdateToDoHandler(event).handler()
