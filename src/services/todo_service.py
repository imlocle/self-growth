from typing import Any, Dict
from repositories.todo_repository import ToDoRepository
from src.models.todo import ToDo
from models.enum import StatusEnum
from utils.helper import generate_id, utc_now_iso


class ToDoService:
    def __init__(self, todo_repo: ToDoRepository = None):
        self.todo_repo = todo_repo or ToDoRepository()

    def create(self, user_id: str, data: dict) -> None:
        timestamp = utc_now_iso()
        todo = ToDo(
            id=generate_id(), date_created=timestamp, date_modified=timestamp, **data
        )
        self.todo_repo.create(user_id, todo)

    def get(self, user_id: str, todo_id: str) -> ToDo | None:
        item = self.todo_repo.get(user_id, todo_id)
        if not item:
            return None
        return ToDo.from_dynamo(item)

    def get_all(self, user_id: str) -> Dict[str, Any]:
        response = self.todo_repo.get_all(user_id)
        return {
            "items": [ToDo.from_dynamo(i) for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey", None),
        }

    def update(self, user_id: str, todo_id: str, data: dict) -> ToDo | None:
        existing = self.todo_repo.get(user_id=user_id, todo_id=todo_id)
        if not existing:
            return None

        # Title
        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Title must be a non-empty string")
        else:
            title = existing.get("title")

        description = data.get("description", existing.get("description"))

        if "status" in data:
            status_raw = data["status"]
            try:
                status = StatusEnum(status_raw)
            except ValueError:
                raise ValueError(
                    f"Invalid status: '{status_raw}'. "
                    f"Expected one of: {[s.value for s in StatusEnum]}"
                )
        else:
            status = existing.get("status")

        updated_todo = ToDo(
            id=existing.get("id"),
            title=title,
            description=description,
            status=status,
            date_created=existing.get("date_created"),
            date_modified=utc_now_iso(),
        )
        self.todo_repo.update(user_id=user_id, todo=updated_todo)
        return updated_todo
