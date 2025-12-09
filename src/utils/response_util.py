import json

from utils.helper import dict_keys_to_camel_case


def get_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization",
    }


def success_response(body: dict, status_code: int = 200):
    body = dict_keys_to_camel_case(body)
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
    }


def error_response(
    message: str,
    status_code: int = 500,
):
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": message}),
    }
