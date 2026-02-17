"""
ToDo controller for handling todo-related requests.
"""

from typing import Any, Dict, Optional

from controllers.base_controller import BaseController
from models.todo import ToDo
from services.todo_service import ToDoService
from utils.request_context import RequestContext
from utils.validation import validate_todo_data


class ToDoController(BaseController):
    """Controller for todo operations"""
    
    def __init__(
        self, 
        event: Dict[str, Any], 
        request_context: RequestContext = None,
        todo_service: ToDoService = None
    ):
        super().__init__(event=event, request_context=request_context, require_auth=True)
        self.todo_service = todo_service or ToDoService()
    
    @property
    def todo_id(self) -> Optional[str]:
        """Todo ID from path parameters"""
        return self.request_context.todo_id
    
    def require_todo_id(self) -> str:
        """Require todo ID from path parameters"""
        return self.request_context.require_todo_id()

    def create(self) -> ToDo:
        """Create a new todo"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        # Validate input data in Controller
        validated_data = validate_todo_data(self.body, is_create=True)
        
        return self.todo_service.create(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            data=validated_data,
        )

    def get(self) -> ToDo:
        """Get a single todo"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        todo_id = self.require_todo_id()

        return self.todo_service.get(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            todo_id=todo_id,
        )

    def get_all(self) -> Dict[str, Any]:
        """Get all todos for a subject"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        sort_by = self.get_query_param("sortBy", "date_modified")
        pagination = self.get_pagination_params()

        from utils.helper import decode_next_token, encode_next_token
        next_token = decode_next_token(pagination.get("next_token"))

        response = self.todo_service.get_all(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            sort_by=sort_by,
            limit=pagination.get("limit"),
            next_token=next_token,
            status=pagination.get("status"),
        )
        return {
            "items": [i.to_dict() for i in response.get("items")],
            "nextToken": encode_next_token(response.get("lastEvaluatedKey")),
        }

    def update(self) -> ToDo:
        """Update an existing todo"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        todo_id = self.require_todo_id()

        # Validate input data in Controller (is_create=False for updates)
        validated_data = validate_todo_data(self.body, is_create=False)

        return self.todo_service.update(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            todo_id=todo_id,
            data=validated_data,
        )

    def delete(self) -> None:
        """Delete a todo"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        todo_id = self.require_todo_id()

        return self.todo_service.delete(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            todo_id=todo_id,
        )
