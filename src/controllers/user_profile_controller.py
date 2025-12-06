from typing import Any, Dict

from models.user_profile import UserProfile
from services.user_profile_service import UserProfileService


class UserProfileController:
    def __init__(self, event, user_profile_service: UserProfileService = None):
        self.event = event
        # Create AuthService to get user_id
        self.user_id = "1"
        self.data = self.validate_data()
        self.user_profile_service = user_profile_service or UserProfileService()

    def validate_data(self) -> Dict[str, Any]:
        return UserProfile.from_event(self.event)

    def create(self) -> UserProfile:
        return self.user_profile_service.create(self.data)

    def get(self) -> UserProfile | None:
        return self.user_profile_service.get(self.user_id)

    def update(self) -> UserProfile | None:
        return self.user_profile_service.update(user_id=self.user_id, data=self.data)
