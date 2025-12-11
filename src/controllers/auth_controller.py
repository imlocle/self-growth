from typing import Any, Dict
from services.auth_service import AuthService
from utils.helper import parse_request_body


class AuthController:
    def __init__(self, event, auth_service: AuthService = None):
        self.event = event
        self.auth_service = auth_service or AuthService()

    def _parse_and_validate(self) -> Dict[str, Any]:
        body = parse_request_body(self.event)
        username = body.get("username") or body.get("phone_number")
        password = body.get("password")

        if not isinstance(username, str) or not username.strip():
            raise ValueError(
                "username or phone_number is required and must be a non-empty string"
            )

        if not isinstance(password, str) or not password.strip():
            raise ValueError("password is required and must be a non-empty string")

        return {
            "username": username.strip(),
            "password": password,
        }

    def login(self) -> Dict[str, Any]:
        """
        Perform login via Cognito and return tokens.
        """
        data = self._parse_and_validate()
        return self.auth_service.login(
            username=data["username"],
            password=data["password"],
        )
