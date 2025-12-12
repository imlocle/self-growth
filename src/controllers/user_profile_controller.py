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
        self.auth_service = AuthService(event=event)
        self.auth_user = self.auth_service.get_auth_user()
        self.user_profile_service = user_profile_service or UserProfileService()

    def create(self) -> UserProfile:
        body = parse_request_body(self.event)
        data = UserProfile.from_dict(
            {
                "email": self.auth_user.email,
                "username": body["username"],
                "first_name": body.get("first_name") or self.auth_user.first_name,
                "last_name": body.get("last_name") or self.auth_user.last_name,
            }
        )
        return self.user_profile_service.create(
            user_id=self.auth_user.user_id, data=data
        )

    def get(self) -> UserProfile:
        return self.user_profile_service.get(self.auth_user.user_id)

    def update(self) -> UserProfile:
        data = parse_request_body(self.event)
        return self.user_profile_service.update(
            user_id=self.auth_user.user_id, data=data
        )
