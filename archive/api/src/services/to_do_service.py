from src.models.to_do import ToDoSchemaRequest, ToDoTable
from sqlalchemy.orm import Session
from src.repositories.to_do_repository import ToDoRepository
from typing import List


class ToDoService:

    def __init__(self, session: Session) -> None:
        self.repo = ToDoRepository(session)

    def create(self, request_todo: ToDoSchemaRequest) -> None:
        try:
            self.repo.create(request_todo)
        except Exception as e:
            raise e

    def get(self, todo_id: int) -> dict:
        return self.repo.get(todo_id).to_dict()

    def get_all(self):
        to_dos: List[ToDoTable] = self.repo.get_all()
        return [todo.to_dict() for todo in to_dos]
