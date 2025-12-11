from typing import Any, Dict

from models.user_profile import UserProfile
from services.auth_service import AuthService
from services.user_profile_service import UserProfileService
from utils.helper import parse_request_body


class UserProfileController:
    def __init__(
        self, event: Dict[str, Any], user_profile_service: UserProfileService = None
    ):
        self.event = event
        self.user_id = AuthService.get_user_id_from_event(event)
        self.user_profile_service = user_profile_service or UserProfileService()

    def create(self) -> UserProfile:
        data = self._validate_data()
        return self.user_profile_service.create(user_id=self.user_id, data=data)

    def get(self) -> UserProfile:
        return self.user_profile_service.get(self.user_id)

    def update(self) -> UserProfile:
        data = parse_request_body(self.event)
        return self.user_profile_service.update(user_id=self.user_id, data=data)

    def _validate_data(self) -> Dict[str, Any]:
        """
        Merge body + Cognito claims, then run through UserProfile.from_dict
        to enforce your strict validation rules.
        """
        body = parse_request_body(self.event)
        claims = AuthService.get_claims(self.event)

        merged = {
            "first_name": body.get("first_name") or claims.get("given_name", ""),
            "last_name": body.get("last_name") or claims.get("family_name", ""),
            "username": (
                body.get("username")
                or claims.get("cognito:username")
                or f"user_{self.user_id[:8]}"
            ),
            "email": body.get("email") or claims.get("email", ""),
            "phone_number": body.get("phone_number") or claims.get("phone_number", ""),
            "points": body.get("points", 0),
            "level": body.get("level", 1),
        }
        return UserProfile.from_dict(merged)
