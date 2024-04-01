from flask import Blueprint, jsonify, request, g
from src.services.to_do_service import ToDoService

TO_DO = Blueprint("TO_DO", __name__)


@TO_DO.post("/to-do/create")
def create():
    service = ToDoService(g.db)
    response = service.create(request.json)
    return jsonify(response.to_dict()), 201


@TO_DO.get("/to-do/list")
def get_all():
    service = ToDoService(g.db)
    todos = service.get_all()
    return jsonify(todos), 200
