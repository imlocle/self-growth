from api.habit.habit import Habit
from api.repository.db_repo import db
from api.utils.constants import POST
from flask import Blueprint, jsonify, request

habit_blueprint = Blueprint("habit", __name__)

@habit_blueprint.route("/create-habit", methods=[POST])
def create_habit():
    req_data = request.get_json(force=True)
    habit = Habit(
        name=req_data["name"],
        user_id=1
    )
    db.session.add(habit)
    db.session.commit()
    return jsonify(habit), 200
        
        
        