import json
from api.utils.constants import POST
from flask import Blueprint, jsonify, request

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/login", methods=[POST])
def login():
    req_data = request.get_json(force=True)
    return jsonify({}), 200

@auth_blueprint.route("/sign-up", methods=[POST])
def sign_up():
    req_data = request.get_json(force=True)
    return jsonify({}), 200

@auth_blueprint.route("/logout")
def logout():
    return jsonify({}), 200
