from typing import Any, Dict, Optional

from controllers.base_controller import BaseController
from models.todo import ToDo
from services.todo_service import ToDoService


class ToDoController(BaseController):
    def __init__(self, event: Dict[str, Any], todo_service: ToDoService | None = None):
        super().__init__(event=event, require_auth=True)

        self.todo_service = todo_service or ToDoService()
        self.todo_id = self._get_todo_id()

    def _get_todo_id(self) -> Optional[str]:
        path = self.event.get("pathParameters") or {}
        return path.get("todoId")

    def _get_query_string(self, param_str: str) -> Optional[str]:
        qs = self.event.get("queryStringParameters") or {}
        return qs.get(param_str)

    def create(self) -> ToDo:
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()

        data = ToDo.from_dict(self.body)
        return self.todo_service.create(
            user_id=self.auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            data=data,
        )

    def get(self) -> ToDo:
        return self.todo_service.get(
            user_id=self.auth_user.user_id,
            household_id=self.household_id,
            subject_id=self.subject_id,
            todo_id=self.todo_id,
        )

    def get_all(self) -> Dict[str, Any]:
        sort_by = self._get_query_string("sortBy") or "date_modified"
        response = self.todo_service.get_all(
            user_id=self.auth_user.user_id,
            household_id=self.household_id,
            subject_id=self.subject_id,
            sort_by=sort_by,
        )
        return {
            "items": [i.to_dict() for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey", None),
        }

    def update(self) -> ToDo:
        return self.todo_service.update(
            user_id=self.auth_user.user_id,
            household_id=self.household_id,
            subject_id=self.subject_id,
            todo_id=self.todo_id,
            data=self.body,
        )

    def delete(self) -> None:
        return self.todo_service.delete(
            user_id=self.auth_user.user_id,
            household_id=self.household_id,
            subject_id=self.subject_id,
            todo_id=self.todo_id,
        )
