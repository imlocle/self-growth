from src.utils.constants import POST
from flask import Blueprint, jsonify, request

habit_blueprint = Blueprint("habit", __name__)


@habit_blueprint.route("/create-habit", methods=[POST])
def create_habit():
    req_data = request.get_json(force=True)
    return 200
