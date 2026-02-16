"""
Household controller for handling household requests.
"""

from typing import Any, Dict

from controllers.base_controller import BaseController
from models.household import Household
from models.household_member import HouseholdMember
from services.household_service import HouseholdService
from services.household_member_service import HouseholdMemberService
from utils.helper import generate_id
from utils.request_context import RequestContext
from utils.validation import validate_household_data


class HouseholdController(BaseController):
    """Controller for household operations"""

    def __init__(
        self,
        event: Dict[str, Any],
        request_context: RequestContext = None,
        household_service: HouseholdService = None,
        member_service: HouseholdMemberService = None,
    ):
        super().__init__(event=event, request_context=request_context, require_auth=True)
        self.household_service = household_service or HouseholdService()
        self.member_service = member_service or HouseholdMemberService()

    def create(self) -> Household:
        """Create a new household and add creator as owner member"""
        validated_data = validate_household_data(self.body, is_create=True)
        household_id = generate_id()

        household = self.household_service.create(
            user_id=self.user_id,
            household_id=household_id,
            data=validated_data,
        )

        # Auto-add creator as owner member
        self.member_service.member_repository.create(
            member=HouseholdMember(
                household_id=household_id,
                user_id=self.user_id,
                role="owner",
                date_created=household.date_created,
                date_modified=household.date_created,
            )
        )

        return household

    def get(self) -> Household:
        """Get a single household"""
        household_id = self.require_household_id()
        return self.household_service.get(
            user_id=self.user_id, household_id=household_id
        )

    def get_all(self) -> Dict[str, Any]:
        """Get all households for the authenticated user"""
        response = self.household_service.get_all_for_user(user_id=self.user_id)
        return {
            "items": [h.to_dict() for h in response.get("items", [])],
        }

    def update(self) -> Household:
        """Update a household"""
        household_id = self.require_household_id()
        validated_data = validate_household_data(self.body, is_create=False)
        return self.household_service.update(
            user_id=self.user_id,
            household_id=household_id,
            data=validated_data,
        )

    def delete(self) -> None:
        """Delete a household"""
        household_id = self.require_household_id()
        self.household_service.delete(
            user_id=self.user_id, household_id=household_id
        )
