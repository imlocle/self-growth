from src.models.exception import NotFoundError
from src.models.habit import HabitSchemaRequest, HabitEventsSchemaRequest
from src.repositories.habit_repository import HabitRepository
from sqlalchemy.orm import Session


class HabitService:
    def __init__(self, session: Session) -> None:
        self.repo = HabitRepository(session)

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

        self.repo.create_habit_event(habit_history)

    def update_habit_event(self, event: HabitEventsSchemaRequest):
        self.repo.update_habit_event(event)
