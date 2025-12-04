from sqlalchemy.orm import Session

from src.models.habit import HabitEventsSchemaRequest
from src.repositories.habit_events_repository import HabitEventsRepository


class HabitEventsService:
    def __init__(self, session: Session) -> None:
        self.event_repo = HabitEventsRepository(session)

    def create_habit_event(self, request_habit_event: HabitEventsSchemaRequest):
        try:
            self.event_repo.create_habit_event(request_habit_event)
        except Exception as e:
            raise e

    def update_habit_event(self, event: HabitEventsSchemaRequest):
        try:
            self.event_repo.update_habit_event(event)
        except Exception as e:
            raise e

    def delete_habit_event(self, habit_id: int):
        try:
            self.event_repo.delete_habit_events(habit_id)
        except Exception as e:
            raise e
