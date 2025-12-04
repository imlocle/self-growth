from sqlalchemy.orm import Session
from src.models.habit import HabitEventsSchemaRequest, HabitEventsTable
from src.repositories.db_repository import DbRepository


class HabitEventsRepository:
    def __init__(self, session: Session) -> None:
        self.db_repo = DbRepository(session)

    def create_habit_event(self, request_event: HabitEventsSchemaRequest) -> None:
        event = HabitEventsTable(**request_event.to_dict())
        self.db_repo.create(event)
        self.db_repo.close()

    def update_habit_event(self, event: HabitEventsSchemaRequest):
        self.db_repo.update(event, HabitEventsTable)
        self.db_repo.close()

    def delete_habit_events(self, habit_id: int):
        events = self.db_repo.get_all_by_habit_id(habit_id, HabitEventsTable)
        for event in events:
            self.db_repo.delete(event.id, HabitEventsTable)
        self.db_repo.close()
