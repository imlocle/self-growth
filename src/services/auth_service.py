from typing import Any, Dict, Optional

from aws.cognito_service import CognitoService
from utils.errors import AuthError


class AuthService:
    def __init__(self, cognito_service=None):
        self.cognito_service = cognito_service or CognitoService()

    def login(self, username: str, password: str) -> Dict[str, Any]:
        return self.cognito_service.initiate_auth(username=username, password=password)

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
            raise AuthError(f"Invalid authorizer context: {e}")

    @staticmethod
    def get_user_id_from_event(event: Dict[str, Any]) -> str:
        """
        Extract the authenticated user id (Cognito sub) from the API Gateway
        event populated by the JWT authorizer.
        """
        claims = AuthService.get_claims(event)
        user_id = claims.get("sub")
        if not user_id:
            raise ValueError("Missing 'sub' claim in JWT")
        return user_id

    @staticmethod
    def get_claim(
        event: Dict[str, Any],
        key: str,
        required: bool = False,
    ) -> Optional[str]:
        """
        Get an arbitrary claim from the JWT (e.g. 'email', 'phone_number').

        If required=True and the claim is missing/empty, raises AuthError.
        """
        claims = AuthService.get_claims(event)
        value = claims.get(key)

        if required and (value is None or value == ""):
            raise AuthError(f"Missing required claim: '{key}'")

        return value
