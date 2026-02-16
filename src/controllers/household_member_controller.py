"""
Household member controller for handling member requests.
"""

from typing import Any, Dict

from controllers.base_controller import BaseController
from models.household_member import HouseholdMember
from services.household_member_service import HouseholdMemberService
from utils.request_context import RequestContext
from utils.validation import validate_household_member_data


class HouseholdMemberController(BaseController):
    """Controller for household member operations"""

    def __init__(
        self,
        event: Dict[str, Any],
        request_context: RequestContext = None,
        member_service: HouseholdMemberService = None,
    ):
        super().__init__(event=event, request_context=request_context, require_auth=True)
        self.member_service = member_service or HouseholdMemberService()

    @property
    def member_user_id(self) -> str | None:
        """Member user ID from path parameters"""
        return self.path_params.get("userId")

    def require_member_user_id(self) -> str:
        """Require member user ID from path parameters"""
        if not self.member_user_id:
            from models.errors import ValidationError
            raise ValidationError(
                "Missing required path parameter: userId", field="userId"
            )
        return self.member_user_id

    def create(self) -> HouseholdMember:
        """Add a member to a household"""
        household_id = self.require_household_id()
        validated_data = validate_household_member_data(self.body)
        return self.member_service.create(
            user_id=self.user_id,
            household_id=household_id,
            data=validated_data,
        )

    def get_all(self) -> Dict[str, Any]:
        """List all members of a household"""
        household_id = self.require_household_id()
        response = self.member_service.get_all(
            user_id=self.user_id, household_id=household_id
        )
        return {
            "items": [m.to_dict() for m in response.get("items", [])],
        }

    def delete(self) -> None:
        """Remove a member from a household"""
        household_id = self.require_household_id()
        member_user_id = self.require_member_user_id()
        self.member_service.delete(
            user_id=self.user_id,
            household_id=household_id,
            member_user_id=member_user_id,
        )
