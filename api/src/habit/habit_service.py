from src import db
from src.habit.habit import Habit


class HabitService:
    def __init__(self) -> None:
        pass

    def create_habit(self, data):
        habit = Habit(name=data["name"], user_id=data["user_id"])
        db.session.add(habit)
        db.session.commit()
