from typing import Any, Dict

from controllers.base_controller import BaseController
from models.household import Household
from models.household_member import HouseholdMember
from models.household_subject import HouseholdSubject
from models.user_profile import UserProfile
from services.household_member_service import HouseholdMemberService
from services.household_service import HouseholdService
from services.household_subject_service import HouseholdSubjectService
from services.user_profile_service import UserProfileService
from utils.helper import generate_id


class UserProfileController(BaseController):
    def __init__(
        self,
        event: Dict[str, Any],
        user_profile_service: UserProfileService = None,
        household_service: HouseholdService = None,
        member_service: HouseholdMemberService = None,
        subject_service: HouseholdSubjectService = None,
    ):
        super().__init__(event=event, require_auth=True)

        self.user_profile_service = user_profile_service or UserProfileService()
        self.household_service = household_service or HouseholdService()
        self.member_service = member_service or HouseholdMemberService()
        self.subject_service = subject_service or HouseholdSubjectService()

    def create(self) -> UserProfile:
        """
        Creates UserProfile + ensures a household + ensures a default subject + membership.
        """
        email = self.body.get("email") or self.auth_user.email
        if not email:
            full = self.auth_service.get_auth_user_from_cognito(event=self.event)
            email = full.email
            self.auth_user = full

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

        if not self.household_service.is_exist(household_id=self.household_id):
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
        return self.user_profile_service.get(user_id=self.auth_user.user_id)

    def update(self) -> UserProfile:
        return self.user_profile_service.update(
            user_id=self.auth_user.user_id, data=self.body
        )

    def create_household(self, household_id: str, name: str) -> None:
        data = Household.from_dict(
            {"name": name, "owner_user_id": self.auth_user.user_id}
        )
        self.household_service.create(household_id=household_id, data=data)

    def create_household_member(self, household_id: str, role: str, username: str):
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
