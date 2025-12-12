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
        self.user_id = AuthService.get_user_id_from_event(event)
        self.user_profile_service = user_profile_service or UserProfileService()

    def create(self) -> UserProfile:
        auth_user = self.auth_service.get_auth_user()
        body = parse_request_body(self.event)
        data = UserProfile.from_dict({"email": auth_user["email"], **body})
        return self.user_profile_service.create(user_id=self.user_id, data=data)

    def get(self) -> UserProfile:
        return self.user_profile_service.get(self.user_id)

    def update(self) -> UserProfile:
        data = parse_request_body(self.event)
        return self.user_profile_service.update(user_id=self.user_id, data=data)
