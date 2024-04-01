from sqlalchemy.orm import Session
from src.models.to_do import ToDoTable

from src.repositories.db_repository import DbRepository


class ToDoRepository:
    def __init__(self, session: Session) -> None:
        self.db_repo = DbRepository(session)

    def create(self, to_do: ToDoTable) -> ToDoTable:
        response: ToDoTable = self.db_repo.create(to_do)
        return response

    def get_all(self):
        return self.db_repo.get_all(ToDoTable)
