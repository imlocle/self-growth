import re
from typing import Any, Dict
from services.auth_service import AuthService
from utils.constants import EMAIL_REGEX, PHONE_REGEX
from utils.helper import parse_request_body


class AuthController:
    def __init__(self, event, auth_service: AuthService = None):
        self.event = event
        self.auth_service = auth_service or AuthService(event=event)

    def _parse_and_validate_login(self) -> Dict[str, Any]:
        body = parse_request_body(self.event)
        username = body.get("username") or body.get("email")
        password = body.get("password")

        if not isinstance(username, str) or not username.strip():
            raise ValueError(
                "username or email is required and must be a non-empty string"
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
        data = self._parse_and_validate_login()
        return self.auth_service.login(
            username=data["username"],
            password=data["password"],
        )

    def _parse_and_validate_signup(self) -> Dict[str, Any]:
        body = parse_request_body(self.event)

        phone_number = body.get("phone_number")
        password = body.get("password")
        email = body.get("email")
        first_name = body.get("first_name")
        last_name = body.get("last_name")

        if phone_number is not None:
            if not isinstance(phone_number, str) or not phone_number.strip():
                raise ValueError("phone_number is required and must be non-empty")

            if not re.match(PHONE_REGEX, phone_number):
                raise ValueError(
                    "Phone number must contain only digits (with optional +) and be 10-15 characters long"
                )

        if not isinstance(password, str) or not password.strip():
            raise ValueError("password is required and must be non-empty")

        if not isinstance(email, str) or not email.strip():
            raise ValueError("email must be a non-empty string if provided")
        if not re.match(EMAIL_REGEX, email):
            raise ValueError(f"Invalid email format: {email}")

        return {
            "email": email,
            "phone_number": phone_number,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        }

    def signup(self) -> Dict[str, Any]:
        data = self._parse_and_validate_signup()
        return self.auth_service.signup(
            email=data["email"],
            phone_number=data["phone_number"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

    def confirm_signup(self) -> Dict[str, Any]:
        data = self._parse_validate_confirm_signup()
        return self.auth_service.confirm_signup(
            email=data["email"], confirmation_code=data["confirmation_code"]
        )

    def _parse_validate_confirm_signup(self) -> Dict[str, Any]:
        body = parse_request_body(self.event)

        email = body.get("email")
        code = body.get("confirmation_code")

        if not isinstance(email, str) or not email.strip():
            raise ValueError("email is required and must be non-empty")
        if not re.match(EMAIL_REGEX, email):
            raise ValueError(f"Invalid email format: {email}")

        if not isinstance(code, str) or not code.strip():
            raise ValueError("confirmation_code is required and must be non-empty")

        if len(code.strip()) < 4:
            raise ValueError("confirmation_code looks too short")

        return {"email": email, "confirmation_code": code.strip()}
