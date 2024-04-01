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
        response = self.repo.get_habit(habit_id)
        if not response:
            raise NotFoundError(f"Habit ID: {habit_id}")
        return response.to_dict()

    def create_habit(self, request_habit: HabitSchemaRequest) -> None:
        habit = self.repo.create_habit(request_habit)
        habit_history = HabitEventsSchemaRequest(
            habit_id=habit.id,
            reset_counter=habit.reset_counter,
        )

        self.event_repo.create_habit_event(habit_history)

    def update_habit_event(self, event: HabitEventsSchemaRequest):
        self.event_repo.update_habit_event(event)

    def delete_habit(self, habit_id: int):
        self.repo.delete_habit(habit_id)
        self.event_repo.delete_habit_events(habit_id)
