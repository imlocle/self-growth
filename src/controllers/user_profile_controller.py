"""
User profile controller for handling user profile operations.
"""

from typing import Any, Dict, Optional

from controllers.base_controller import BaseController
from models.user_profile import UserProfile
from models.errors import AuthenticationError
from services.auth_service import AuthService
from services.user_profile_service import UserProfileService
from utils.request_context import RequestContext


class UserProfileController(BaseController):
    """Controller for user profile CRUD operations"""

    def __init__(
        self,
        event: Dict[str, Any],
        request_context: Optional[RequestContext] = None,
        user_profile_service: Optional[UserProfileService] = None,
        auth_service: Optional[AuthService] = None,
    ):
        super().__init__(event=event, request_context=request_context, require_auth=True)
        self.user_profile_service = user_profile_service or UserProfileService()
        self.auth_service = auth_service or AuthService()

    def create(self) -> UserProfile:
        """Create a user profile."""
        auth_user = self.request_context.require_auth()

        data = UserProfile.from_dict(
            {
                "username": self.body.get("username"),
                "first_name": self.body.get("first_name") or auth_user.first_name,
                "last_name": self.body.get("last_name") or auth_user.last_name,
                "phone_number": self.body.get("phone_number"),
            }
        )

        return self.user_profile_service.create(
            user_id=auth_user.user_id,
            data=data,
        )

    def get(self) -> UserProfile:
        """Get user profile"""
        auth_user = self.request_context.require_auth()
        return self.user_profile_service.get(user_id=auth_user.user_id)

    def update(self) -> UserProfile:
        """Update user profile"""
        auth_user = self.request_context.require_auth()
        return self.user_profile_service.update(
            user_id=auth_user.user_id, data=self.body
        )

    def _extract_access_token(self) -> str:
        """Extract access token from Authorization header."""
        headers = self.event.get("headers") or {}
        auth_header = headers.get("authorization") or headers.get("Authorization") or ""

        if not auth_header:
            raise AuthenticationError("Missing Authorization header")

        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]

        return auth_header
