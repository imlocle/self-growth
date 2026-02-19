import json

from utils.helper import dict_keys_to_camel_case

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key",
}


def get_headers() -> dict[str, str]:
    return {**CORS_HEADERS}


def success_response(body: dict, status_code: int = 200):
    camel_case_body = dict_keys_to_camel_case(body)
    return {
        "statusCode": status_code,
        "headers": get_headers(),
        "body": json.dumps(camel_case_body),
    }


def error_response(
    message: str = "Internal server error",
    status_code: int = 500,
):
    print(message)
    message = "Internal server error" if status_code == 500 else message
    return {
        "statusCode": status_code,
        "headers": get_headers(),
        "body": json.dumps({"error": message}),
    }
