import json
from typing import Any, Dict
from services.todo_service import ToDoService
from models.to_do import ToDo


class ToDoController:
    def __init__(self, event, todo_service: ToDoService = None):
        self.event = event
        body_str = event.get("body") or "{}"
        # Create AuthService to get user_id
        self.user_id = "1"
        self.body = json.loads(body_str)
        self.todo_service = todo_service or ToDoService()

    def create(self) -> None:
        self.todo_service.create(self.user_id, self.body)

    def get(self) -> ToDo | None:
        todo_id = self.event.get("pathParameters", {}).get("todoId")
        return self.todo_service.get(self.user_id, todo_id)

    def get_all(self) -> Dict[str, Any]:
        response = self.todo_service.get_all(self.user_id)
        return {
            "items": [i.to_dict() for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey", None),
        }

    def update(self) -> ToDo | None:
        todo_id = self.event.get("pathParameters", {}).get("todoId")
        return self.todo_service.update(
            user_id=self.user_id, todo_id=todo_id, data=self.body
        )
