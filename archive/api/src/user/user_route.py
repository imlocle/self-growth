from flask import Blueprint, request, jsonify
from src.user.user_service import UserService

user_blueprint = Blueprint("user", __name__)
user_service = UserService()


@user_blueprint.route("/user/<username>/profile")
def profile(username):
    user = user_service.get_user(username)
    response = {"id": user.id, "username": user.username, "email": user.email}
    return jsonify(response), 200
