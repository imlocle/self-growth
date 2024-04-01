from sqlalchemy.orm import Session
from src.models.habit import (
    HabitEventsSchemaResponse,
    HabitEventsTable,
    HabitSchemaResponse,
    HabitTable,
    HabitSchemaRequest,
    HabitEventsSchemaRequest,
)
from src.repositories.db_repository import DbRepository


class HabitRepository:
    def __init__(self, session: Session) -> None:
        self.db_repo = DbRepository(session)

    def get_habit(self, habit_id: str) -> HabitSchemaResponse | None:
        habit = None
        habit_history = []
        response = self.db_repo.get_join(habit_id, HabitTable, HabitEventsTable)[0]
        for data in response:
            if isinstance(data, HabitTable):
                habit = HabitSchemaResponse.from_dict(data.__dict__)
            elif isinstance(data, HabitEventsTable):
                habit_history.append(HabitEventsSchemaResponse.from_dict(data.__dict__))
        habit.habit_events = habit_history

        return habit

    def create_habit(self, request_habit: HabitSchemaRequest) -> HabitSchemaResponse:
        habit = HabitTable(**request_habit.to_dict())
        self.db_repo.create(habit, False)
        return HabitSchemaResponse.from_dict(
            {"id": habit.id, **request_habit.to_dict()}
        )

    def create_habit_event(self, request_event: HabitEventsSchemaRequest) -> None:
        event = HabitEventsTable(**request_event.to_dict())
        self.db_repo.create(event)

    def update_habit_event(self, event: HabitEventsSchemaRequest):
        self.db_repo.update(event, HabitEventsTable)
