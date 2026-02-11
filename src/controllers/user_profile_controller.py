"""
User profile controller for handling user profile operations.
"""

from typing import Any, Dict

from controllers.base_controller import BaseController
from models.household import Household
from models.household_member import HouseholdMember
from models.household_subject import HouseholdSubject
from models.user_profile import UserProfile
from models.errors import AuthenticationError
from services.auth_service import AuthService
from services.household_member_service import HouseholdMemberService
from services.household_service import HouseholdService
from services.household_subject_service import HouseholdSubjectService
from services.user_profile_service import UserProfileService
from utils.request_context import RequestContext
from utils.helper import generate_id


class UserProfileController(BaseController):
    """Controller for user profile operations"""
    
    def __init__(
        self,
        event: Dict[str, Any],
        request_context: RequestContext = None,
        user_profile_service: UserProfileService = None,
        household_service: HouseholdService = None,
        member_service: HouseholdMemberService = None,
        subject_service: HouseholdSubjectService = None,
        auth_service: AuthService = None,
    ):
        super().__init__(event=event, request_context=request_context, require_auth=True)

        self.user_profile_service = user_profile_service or UserProfileService()
        self.household_service = household_service or HouseholdService()
        self.member_service = member_service or HouseholdMemberService()
        self.subject_service = subject_service or HouseholdSubjectService()
        self.auth_service = auth_service or AuthService()

    def create(self) -> UserProfile:
        """
        Creates UserProfile + ensures a household + ensures a default subject + membership.
        """
        # Get email from body, auth_user claims, or fetch from Cognito
        email = self.body.get("email") or self.auth_user.email
        if not email:
            # Email not in JWT claims, fetch from Cognito
            access_token = self._extract_access_token()
            full_user = self.auth_service.get_user_from_cognito(access_token)
            email = full_user.email
            if not email:
                raise AuthenticationError("Email not found in Cognito user attributes")

        user_id = self.auth_user.user_id

        username = self.body.get("username")
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username is required and must be non-empty")

        household_id = self.body.get("household_id") or generate_id()
        subject_id = generate_id()

        role = self.body.get("role", "MEMBER")
        subject_type = self.body.get("type", "DEPENDENT")

        data = UserProfile.from_dict(
            {
                "email": email,
                "username": username,
                "first_name": self.body.get("first_name") or self.auth_user.first_name,
                "last_name": self.body.get("last_name") or self.auth_user.last_name,
            }
        )
        user_profile = self.user_profile_service.create(
            user_id=user_id, household_id=household_id, subject_id=subject_id, data=data
        )

        if not self.household_service.is_exist(household_id=household_id):
            role = "OWNER"
            subject_type = "SELF"
            household_name = (
                self.body.get("household_name") or f"{username}'s Household"
            )
            self.create_household(household_id=household_id, name=household_name)

        self.create_household_member(
            household_id=household_id, role=role, username=username
        )
        self.create_household_subject(
            household_id=household_id,
            subject_id=subject_id,
            subject_type=subject_type,
            username=username,
        )

        return user_profile

    def get(self) -> UserProfile:
        """Get user profile"""
        return self.user_profile_service.get(user_id=self.auth_user.user_id)

    def update(self) -> UserProfile:
        """Update user profile"""
        return self.user_profile_service.update(
            user_id=self.auth_user.user_id, data=self.body
        )

    def create_household(self, household_id: str, name: str) -> None:
        """Create a household"""
        data = Household.from_dict(
            {"name": name, "owner_user_id": self.auth_user.user_id}
        )
        self.household_service.create(household_id=household_id, data=data)

    def create_household_member(self, household_id: str, role: str, username: str):
        """Create a household member"""
        data = HouseholdMember.from_dict(
            {
                "household_id": household_id,
                "user_id": self.auth_user.user_id,
                "role": role,
                "display_name": self.body.get("display_name") or username,
                **self.body,
            }
        )
        self.member_service.create(data=data)

    def create_household_subject(
        self,
        household_id: str,
        subject_id: str,
        subject_type: str,
        username: str,
    ) -> None:
        """Create a household subject"""
        data = HouseholdSubject.from_dict(
            {
                "household_id": household_id,
                "user_id": self.auth_user.user_id,
                "type": subject_type,
                "display_name": self.body.get("display_name") or username,
                **self.body,
            }
        )
        self.subject_service.create(subject_id=subject_id, data=data)

    def _extract_access_token(self) -> str:
        """
        Extract access token from Authorization header.
        
        Returns:
            Access token string
            
        Raises:
            AuthenticationError: Missing or invalid Authorization header
        """
        headers = self.event.get("headers") or {}
        auth_header: str = headers.get("authorization") or headers.get("Authorization")

        if not auth_header:
            raise AuthenticationError("Missing Authorization header")

        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]

        return auth_header
