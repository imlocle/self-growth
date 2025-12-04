from src.services.auth_service import AuthService
from src.utils.constants import POST
from flask import Blueprint, jsonify, request

AUTH = Blueprint("AUTH", __name__)
service = AuthService()


@AUTH.route("/login", methods=[POST])
def login():
    req_data = request.get_json(force=True)
    return jsonify({}), 200


@AUTH.route("/sign-up", methods=[POST])
def sign_up():
    req_data = request.get_json(force=True)
    user = service.sign_up(data=req_data)
    return jsonify({"id": user.id, "email": user.email, "username": user.username}), 200


@AUTH.route("/logout")
def logout():
    return jsonify({}), 200
