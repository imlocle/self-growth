from typing import List
from sqlalchemy.orm import Session
from src.models.exception import NotFoundError
from src.models.habit import (
    HabitSchemaRequest,
    HabitSchemaResponse,
)
from src.repositories.habit_repository import HabitRepository


class HabitService:
    def __init__(self, session: Session) -> None:
        self.repo = HabitRepository(session)

    def get_all(self) -> List[HabitSchemaResponse]:
        try:
            response = self.repo.get_all()
            habits = [HabitSchemaResponse.from_dict(data.__dict__) for data in response]
            return habits
        except Exception as e:
            raise NotFoundError(e)

    def get(self, habit_id: int) -> HabitSchemaResponse:
        try:
            response = self.repo.get(habit_id)
            return HabitSchemaResponse.from_dict(response.__dict__)
        except Exception as e:
            raise NotFoundError(e)

    def create_habit(self, request_habit: HabitSchemaRequest) -> HabitSchemaResponse:
        try:
            return self.repo.create_habit(request_habit)
        except Exception as e:
            raise e

    def delete_habit(self, habit_id: int):
        try:
            self.repo.delete_habit(habit_id)
        except Exception as e:
            raise e
