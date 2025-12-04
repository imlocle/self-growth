from flask import jsonify
from src.models.exception import PY_ERROR_TYPES, BadRequestError


def exception_handler(exception):
    if type(exception) in PY_ERROR_TYPES:
        exception = BadRequestError(message=str(exception))
    return jsonify(message=exception.message, status=exception.status), exception.status
