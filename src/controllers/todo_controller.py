from typing import Any, Dict

from models.todo import ToDo
from services.todo_service import ToDoService


class ToDoController:
    def __init__(self, event: Dict[str, Any], todo_service: ToDoService = None):
        self.event = event
        # Create AuthService to get user_id
        self.user_id = "1"
        self.todo_service = todo_service or ToDoService()

    def validate_data(self) -> Dict[str, Any]:
        return ToDo.from_event(self.event)

    def create(self) -> ToDo:
        data = self.validate_data()
        return self.todo_service.create(self.user_id, data)

    def get(self) -> ToDo:
        todo_id = self._get_path_params_id()
        return self.todo_service.get(self.user_id, todo_id)

    def get_all(self) -> Dict[str, Any]:
        response = self.todo_service.get_all(self.user_id)
        return {
            "items": [i.to_dict() for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey", None),
        }

    def update(self) -> ToDo:
        data = self.validate_data()
        todo_id = self._get_path_params_id()
        return self.todo_service.update(
            user_id=self.user_id, todo_id=todo_id, data=data
        )

    def delete(self) -> None:
        todo_id = self._get_path_params_id()
        return self.todo_service.delete(self.user_id, todo_id)

    def _get_path_params_id(self) -> str:
        return self.event.get("pathParameters", {}).get("todoId")
