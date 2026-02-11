"""
Lambda handler for deleting a todo.
"""

from typing import Dict, Any

from controllers.todo_controller import ToDoController
from utils.response_util import success_response
from handlers.base_handler import BaseHandler, lambda_handler_with_errors


class DeleteToDoHandler(BaseHandler):
    """Handler for DELETE /households/{householdId}/subjects/{subjectId}/todos/{todoId}"""
    
    def __init__(self, event: Dict[str, Any]):
        super().__init__(event)
        # Share RequestContext with Controller
        self.controller = ToDoController(event, request_context=self.request_context)

    def handler(self):
        return self.handle_with_logging("delete_todo", self._delete_todo)
    
    def _delete_todo(self):
        """Delete a todo (soft delete)"""
        self.controller.delete()
        return success_response(body={}, status_code=204)


@lambda_handler_with_errors("delete_todo")
def lambda_handler(event, context):
    return DeleteToDoHandler(event).handler()
