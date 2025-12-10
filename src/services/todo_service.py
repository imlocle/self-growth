from typing import Any, Dict

from models.enum import ToDoStatusEnum
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
        existing = self.todo_repo.get(user_id=user_id, todo_id=todo_id)
        if not existing:
            raise NotFoundError("Not Found")

        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Title must be a non-empty string")
        else:
            title = existing["title"]

        description = data.get("description", existing.get("description"))

        if "status" in data:
            status = parse_enum(ToDoStatusEnum, data["status"])
        else:
            status = ToDoStatusEnum(existing["status"])

        updated_todo = ToDo(
            id=existing["id"],
            title=title,
            description=description,
            status=status,
            date_created=existing["date_created"],
            date_modified=utc_now_iso(),
        )
        self.todo_repo.update(user_id=user_id, todo=updated_todo)
        return updated_todo

    def delete(self, user_id: str, todo_id: str) -> None:
        existing = self.todo_repo.get(user_id=user_id, todo_id=todo_id)
        if not existing:
            raise NotFoundError("Not Found")

        deleted_todo = ToDo(
            id=existing["id"],
            title=existing["title"],
            description=existing["description"],
            status=ToDoStatusEnum.DELETED,
            date_created=existing["date_created"],
            date_modified=utc_now_iso(),
        )
        self.todo_repo.update(user_id=user_id, todo=deleted_todo)
