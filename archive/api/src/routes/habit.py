from flask import Blueprint, jsonify, request
from src.models.enum import StatusEnum
from src.database.session import get_db_session
from src.models.habit import HabitSchemaRequest
from src.repositories.db_repository import DB_PATH
from src.services.habit_service import HabitService

HABIT = Blueprint("HABIT", __name__)

habit_service = HabitService(get_db_session(DB_PATH))


@HABIT.get("/habit/<habit_id>")
def get(habit_id: int):
    return jsonify(habit_service.get(habit_id)), 200


@HABIT.get("/habits")
def get_all():
    return jsonify(habit_service.get_all()), 200


@HABIT.post("/habit/create")
def create_habit():
    habit = HabitSchemaRequest.from_dict({"status": StatusEnum.new, **request.json})
    return jsonify(habit_service.create_habit(habit)), 201

@HABIT.delete("/habit/<habit_id>/delete")
def delete_habit(habit_id: int):
    habit_service.delete_habit(habit_id)
    return {}, 204
