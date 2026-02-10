from typing import Any, Dict, Optional

from aws.cognito_service import CognitoService
from models.auth import AuthUser
from models.errors import AuthorizationError


class AuthService:
    def __init__(self, cognito_service: CognitoService = None):
        self.cognito_service = cognito_service or CognitoService()

    def login(self, username: str, password: str) -> Dict[str, Any]:
        return self.cognito_service.initiate_auth(username=username, password=password)

    def signup(
        self,
        email: str,
        password: str,
        phone_number: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        return self.cognito_service.sign_up(
            email=email,
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

    def confirm_signup(self, email: str, confirmation_code: str) -> Dict[str, Any]:
        return self.cognito_service.confirm_sign_up(email, confirmation_code)

    def get_auth_user_from_cognito(self, event: Dict[str, Any]) -> AuthUser:
        response = self.cognito_service.get_user(
            access_token=self.get_access_token(event=event)
        )
        return AuthUser.from_cognito(response)

    @staticmethod
    def get_auth_user_from_claims(event: Dict[str, Any]) -> AuthUser:
        claims = AuthService.get_claims(event)

        user_id = claims.get("sub") or claims.get("username")
        if not user_id:
            raise AuthorizationError("Missing 'sub' claim in JWT")

        return AuthUser(
            user_id=user_id,
            attributes=claims,
        )

    @staticmethod
    def get_access_token(event: Dict[str, Any]) -> str:
        headers = event.get("headers") or {}
        auth_header: str = headers.get("authorization") or headers.get("Authorization")

        if not auth_header:
            raise ValueError("Missing Authorization header")

        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]

        return auth_header

    @staticmethod
    def get_claims(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract JWT claims from an API Gateway HTTP API event
        when using a Cognito JWT authorizer.
        """
        try:
            return (
                event.get("requestContext", {})
                .get("authorizer", {})
                .get("jwt", {})
                .get("claims", {})
            ) or {}
        except Exception as e:
            raise AuthorizationError(f"Invalid authorizer context: {e}")

    @staticmethod
    def get_claim(
        event: Dict[str, Any],
        key: str,
        required: bool = False,
    ) -> Optional[str]:
        """
        Get an arbitrary claim from the JWT (e.g. 'email', 'phone_number').

        If required=True and the claim is missing/empty, raises AuthorizationError.
        """
        claims = AuthService.get_claims(event)
        value = claims.get(key)

        if required and (value is None or value == ""):
            raise AuthorizationError(f"Missing required claim: '{key}'")

        return value
