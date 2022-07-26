from src import db
from flask import Blueprint, jsonify, request
from src.to_do.to_do_service import ToDoService
from src.utils.constants import GET, POST

to_do_blueprint = Blueprint("to_do", __name__)

@to_do_blueprint.route("/user/<username>/to-do/create", methods=[POST])
def create_to_do(username):
    req_data = request.get_json(force=True)
    to_do_service = ToDoService()
    response = to_do_service.create_to_do(req_data)
    return jsonify(response), 200

@to_do_blueprint.route("/user/<username>/to-do/list", methods=[GET])
def list_to_do(username):
    return "hello"