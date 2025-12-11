from typing import Any, Dict

from models.todo import ToDo
from services.todo_service import ToDoService
from services.auth_service import AuthService
from utils.helper import parse_request_body


class ToDoController:
    def __init__(self, event: Dict[str, Any], todo_service: ToDoService = None):
        self.event = event
        self.user_id = AuthService.get_user_id_from_event(event)
        self.todo_service = todo_service or ToDoService()

    def create(self) -> ToDo:
        body = parse_request_body(self.event)
        data = ToDo.from_dict(body)
        return self.todo_service.create(self.user_id, data)

    def get(self) -> ToDo:
        todo_id = self._get_path_params_id()
        return self.todo_service.get(self.user_id, todo_id)

    def get_all(self) -> Dict[str, Any]:
        sort_by = self._get_query_string("sortBy") or "date_modified"
        response = self.todo_service.get_all(self.user_id, sort_by)

        return {
            "items": [i.to_dict() for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey", None),
        }

    def update(self) -> ToDo:
        data = parse_request_body(self.event)
        todo_id = self._get_path_params_id()
        return self.todo_service.update(
            user_id=self.user_id, todo_id=todo_id, data=data
        )

    def delete(self) -> None:
        todo_id = self._get_path_params_id()
        return self.todo_service.delete(self.user_id, todo_id)

    def _get_path_params_id(self) -> str:
        return self.event.get("pathParameters", {}).get("todoId")

    def _get_query_string(self, param_str: str) -> str | None:
        qs = self.event.get("queryStringParameters") or {}
        return qs.get(param_str)
