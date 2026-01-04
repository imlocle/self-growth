from typing import Any, Dict, Optional

from models.auth import AuthUser
from services.auth_service import AuthService
from utils.errors import AuthError
from utils.helper import parse_request_body


class BaseController:
    def __init__(
        self,
        event: Dict[str, Any],
        auth_service: AuthService = None,
        require_auth: bool = True,
    ):
        self.event = event
        self.auth_service = auth_service or AuthService()

        self.body = parse_request_body(event)

        self.household_id = self._get_household_id()
        self.subject_id = self._get_subject_id()

        self.auth_user: Optional[AuthUser] = None
        if require_auth:
            self.auth_user = self._build_auth_user()

    def _build_auth_user(self) -> AuthUser:
        try:
            return AuthService.get_auth_user_from_claims(event=self.event)
        except AuthError:
            return self.auth_service.get_auth_user_from_cognito(event=self.event)

    def _get_household_id(self) -> Optional[str]:
        path = self.event.get("pathParameters") or {}
        return path.get("householdId")

    def _get_subject_id(self) -> Optional[str]:
        path = self.event.get("pathParameters") or {}
        return path.get("subjectId")

    def require_household_id(self) -> str:
        if not self.household_id:
            raise AuthError("Missing householdId")
        return self.household_id

    def require_subject_id(self) -> str:
        if not self.subject_id:
            raise AuthError("Missing subjectId")
        return self.subject_id
