from flask import Blueprint, jsonify, request
from src.models.habit import HabitEventsSchemaRequest
from src.services.habit_events_service import HabitEventsService
from src.database.session import get_db_session
from src.repositories.db_repository import DB_PATH

HABIT_EVENTS = Blueprint("HABIT_EVENTS", __name__)

habit_events_service = HabitEventsService(get_db_session(DB_PATH))


@HABIT_EVENTS.patch("/habit/event/update")
def update_habit_event():
    event = HabitEventsSchemaRequest.from_dict(request.json)
    habit_events_service.update_habit_event(event)
    return {}, 204


@HABIT_EVENTS.post("/habit/event/create")
def create_habit_event():
    event = HabitEventsSchemaRequest.from_dict(**request.json)
    habit_events_service.create_habit_event(event)
    return jsonify("Created"), 201
