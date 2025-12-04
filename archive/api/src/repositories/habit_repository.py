from typing import List
from sqlalchemy.orm import Session
from src.models.habit import (
    HabitSchemaResponse,
    HabitTable,
    HabitSchemaRequest,
    HabitEventsSchemaResponse,
    HabitEventsTable,
)
from src.repositories.db_repository import DbRepository


class HabitRepository:
    def __init__(self, session: Session) -> None:
        self.db_repo = DbRepository(session)

    def get_all(self) -> List[HabitTable] | None:
        response = self.db_repo.get_all(HabitTable)
        self.db_repo.close()
        return response

    def get(self, habit_id: int) -> HabitSchemaResponse | None:
        response = self.db_repo.get(habit_id, HabitTable)
        self.db_repo.close()
        return response

    def create_habit(self, request_habit: HabitSchemaRequest) -> HabitSchemaResponse:
        habit = HabitTable(**request_habit.to_dict())
        self.db_repo.create(habit)
        return HabitSchemaResponse.from_dict(
            {"id": habit.id, **request_habit.to_dict()}
        )

    def delete_habit(self, habit_id: int):
        self.db_repo.delete(habit_id, HabitTable)
