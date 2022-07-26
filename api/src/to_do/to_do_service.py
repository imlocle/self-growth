from src.to_do.to_do import ToDo
from src import db

class ToDoService:
    def __init__(self) -> None:
        pass
    
    def create_to_do(self, data):
        todo = ToDo(todo=data["todo"], user_id=data["user_id"])
        db.session.add(todo)
        db.session.commit()
        return "completed"