from src.models.to_do import ToDoTable
from sqlalchemy.orm import Session
from datetime import datetime
from src.repositories.to_do_repository import ToDoRepository
from typing import List


class ToDoService:

    def __init__(self, session: Session) -> None:
        self.todo_repo = ToDoRepository(session)

    def create(self, data: dict) -> ToDoTable:
        text: str = data["text"] if data["text"] is not None else None
        date_due = data["date_due"] if data["date_due"] is not None else None

        if date_due:
            date_due = datetime.fromisoformat(date_due)
        to_do = ToDoTable(title=data["title"], text=text, date_due=date_due)
        response = self.todo_repo.create(to_do)
        return response

    def get_all(self):
        to_dos: List[ToDoTable] = self.todo_repo.get_all()
        return [todo.to_dict() for todo in to_dos]
