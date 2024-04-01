from sqlalchemy.orm import Session
from src.models.to_do import ToDoSchemaResponse, ToDoTable, ToDoSchemaRequest

from src.repositories.db_repository import DbRepository


class ToDoRepository:
    def __init__(self, session: Session) -> None:
        self.db_repo = DbRepository(session)

    def create(self, request_todo: ToDoSchemaRequest) -> None:
        todo = ToDoTable(**request_todo.to_dict())
        self.db_repo.create(todo)
        self.db_repo.close()

    def get_all(self):
        response = self.db_repo.get_all(ToDoTable)
        self.db_repo.close()
        return response

    def get(self, todo_id: int) -> ToDoSchemaResponse:
        response = self.db_repo.get(todo_id, ToDoTable)
        todo = ToDoSchemaResponse.from_dict(response.__dict__)
        self.db_repo.close()
        return todo
