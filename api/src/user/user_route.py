from flask import Blueprint, request, jsonify

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/user/<username>/profile")
def profile():
    response = {"name": "Loc", "about": "Hello! I am a software engineer."}
    return jsonify(response), 200
