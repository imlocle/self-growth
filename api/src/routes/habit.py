from flask import Blueprint, jsonify, request
from src.database.session import get_db_session
from src.models.habit import HabitEventsSchemaRequest, HabitSchemaRequest
from src.repositories.db_repository import DB_PATH
from src.services.habit_service import HabitService

HABIT = Blueprint("HABIT", __name__)

habit_service = HabitService(get_db_session(DB_PATH))


@HABIT.get("/habit/<habit_id>")
def get(habit_id: int):
    return jsonify(habit_service.get_habit(habit_id)), 200


@HABIT.post("/habit/create")
def create_habit():
    habit = HabitSchemaRequest.from_dict({"status": "new", **request.json})
    habit_service.create_habit(habit)
    return jsonify("Created"), 201


@HABIT.patch("/habit/update/event")
def update_habit_event():
    event = HabitEventsSchemaRequest.from_dict(request.json)
    habit_service.update_habit_event(event)
    return {}, 204


@HABIT.post("/habit/event/create")
def create_habit_event():
    event = HabitEventsSchemaRequest.from_dict(**request.json)
    habit_service.create_habit_event(event)
    return jsonify("Created"), 201


@HABIT.delete("/habit/<habit_id>/delete")
def delete_habit(habit_id: int):
    habit_service.delete_habit(habit_id)
    return {}, 204
