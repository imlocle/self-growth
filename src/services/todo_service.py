from typing import Any, Dict

from models.enum import DifficultyEnum, ToDoStatusEnum
from models.todo import ToDo
from repositories.todo_repository import ToDoRepository
from utils.error_util import NotFoundError
from utils.helper import generate_id, parse_enum, parse_iso, utc_now_iso


class ToDoService:
    def __init__(self, todo_repo: ToDoRepository = None):
        self.todo_repo = todo_repo or ToDoRepository()

    def create(self, user_id: str, data: dict) -> ToDo:
        timestamp = utc_now_iso()

        todo = ToDo(
            id=generate_id(), date_created=timestamp, date_modified=timestamp, **data
        )
        self.todo_repo.create(user_id, todo)

        return todo

    def get(self, user_id: str, todo_id: str) -> ToDo:
        item = self.todo_repo.get(user_id, todo_id)
        if not item:
            raise NotFoundError("Not Found")

        return ToDo.from_dynamo(item)

    def get_all(self, user_id: str, sort_by: str = "date_modifed") -> Dict[str, Any]:
        response = self.todo_repo.get_all(user_id)
        items = [ToDo.from_dynamo(i) for i in response.get("items")]

        if sort_by == "date_due":
            items.sort(
                key=lambda t: (
                    t.date_due is None,
                    parse_iso(t.date_due or t.date_modified),
                )
            )
        else:
            items.sort(key=lambda t: parse_iso(t.date_modified))

        return {
            "items": items,
            "lastEvaluatedKey": response.get("lastEvaluatedKey"),
        }

    def update(self, user_id: str, todo_id: str, data: dict) -> ToDo:
        todo = self.get(user_id=user_id, todo_id=todo_id)

        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("title must be a non-empty string")
            todo.title = title

        if "checklist" in data:
            checklist = data["checklist"]
            if not isinstance(checklist, list):
                raise ValueError("checklist must be a list of strings")
            if not all(isinstance(item, str) and item.strip() for item in checklist):
                raise ValueError("checklist must contain only non-empty strings")
            todo.checklist = checklist

        todo.description = data.get("description", todo.description)

        if "difficulty" in data:
            todo.difficulty = parse_enum(DifficultyEnum, data["difficulty"])

        if "status" in data:
            todo.status = parse_enum(ToDoStatusEnum, data["status"])

        self.todo_repo.update(user_id=user_id, todo=todo)
        return todo

    def delete(self, user_id: str, todo_id: str) -> None:
        todo = self.get(user_id=user_id, todo_id=todo_id)
        todo.status = ToDoStatusEnum.DELETED

        self.todo_repo.update(user_id=user_id, todo=todo)
