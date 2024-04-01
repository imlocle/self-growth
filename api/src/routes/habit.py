from src.repositories.db_repository import DB_PATH
from src.database.session import get_db_session
from src.models.habit import HabitEventsSchemaRequest, HabitSchemaRequest
from src.services.habit_service import HabitService
from flask import Blueprint, jsonify, request

HABIT = Blueprint("HABIT", __name__)

service = HabitService(get_db_session(DB_PATH))


@HABIT.get("/habit/<habit_id>")
def get(habit_id: int):
    return jsonify(service.get_habit(habit_id)), 200


@HABIT.post("/habit/create")
def create_habit():
    habit = HabitSchemaRequest.from_dict(request.json)
    service.create_habit(habit)
    return jsonify("Created"), 201


@HABIT.patch("/habit/update/event")
def update_habit_event():
    event = HabitEventsSchemaRequest.from_dict(request.json)
    service.update_habit_event(event)
    return {}, 204
