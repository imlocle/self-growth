import json

def get_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization",
    }

def success_response(body: dict, status_code: int = 200):
    return {
        "statusCode": status_code,
        "headers": get_headers(),
        "body": json.dumps(body),
    }

def error_response(
    message: str,
    headers: dict,
    status_code: int = 400,
):
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps({"error": message}),
    }