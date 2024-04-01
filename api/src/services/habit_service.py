from sqlalchemy.orm import Session
from src.models.exception import NotFoundError
from src.models.habit import HabitSchemaRequest, HabitEventsSchemaRequest
from src.repositories.habit_events_repository import HabitEventsRepository
from src.repositories.habit_repository import HabitRepository


class HabitService:
    def __init__(self, session: Session) -> None:
        self.repo = HabitRepository(session)
        self.event_repo = HabitEventsRepository(session)

    def get_habit(self, habit_id: int) -> dict:
        try:
            return self.repo.get_habit(habit_id).to_dict()
        except Exception as e:
            raise NotFoundError(e)

    def create_habit(self, request_habit: HabitSchemaRequest) -> None:
        try:
            habit = self.repo.create_habit(request_habit)
            habit_event = HabitEventsSchemaRequest(
                habit_id=habit.id,
                reset_counter=habit.reset_counter,
            )

            self.event_repo.create_habit_event(habit_event)
        except Exception as e:
            raise e

    def create_habit_event(self, request_habit_event: HabitEventsSchemaRequest):
        try:
            self.get_habit(request_habit_event.habit_id)
            self.event_repo.create_habit_event(request_habit_event)
        except Exception as e:
            raise e

    def update_habit_event(self, event: HabitEventsSchemaRequest):
        try:
            self.event_repo.update_habit_event(event)
        except Exception as e:
            raise e

    def delete_habit(self, habit_id: int):
        try:
            self.repo.delete_habit(habit_id)
            self.event_repo.delete_habit_events(habit_id)
        except Exception as e:
            raise e
