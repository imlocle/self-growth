from flask import Blueprint, jsonify, request
from src.models.to_do import ToDoSchemaRequest
from src.database.session import get_db_session
from src.repositories.db_repository import DB_PATH
from src.services.to_do_service import ToDoService

TO_DO = Blueprint("TO_DO", __name__)
service = ToDoService(get_db_session(DB_PATH))


@TO_DO.post("/to-do/create")
def create():
    to_do = ToDoSchemaRequest.from_dict({"status": "new", **request.json})
    service.create(to_do)
    return jsonify("Created"), 201


@TO_DO.get("/to-do/<todo_id>")
def get(todo_id: int):
    return jsonify(service.get(todo_id)), 200
