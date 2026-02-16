from typing import Any, Dict
from models.errors import ConflictError, NotFoundError
from models.household_member import HouseholdMember
from repositories.household_member_repository import HouseholdMemberRepository
from services.access_service import AccessService
from utils.helper import utc_now_iso


class HouseholdMemberService:
    def __init__(
        self,
        member_repository: HouseholdMemberRepository = None,
        access_service: AccessService = None,
    ):
        self.member_repository = member_repository or HouseholdMemberRepository()
        self.access = access_service or AccessService()

    def create(self, user_id: str, household_id: str, data: Dict[str, Any]) -> HouseholdMember:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)

        # Check if member already exists
        existing = self.member_repository.get(
            household_id=household_id, user_id=data["user_id"]
        )
        if existing:
            raise ConflictError(
                message="User is already a member of this household",
                resource_type="household_member",
                conflict_field="user_id",
            )

        timestamp = utc_now_iso()
        member = HouseholdMember(
            household_id=household_id,
            date_created=timestamp,
            date_modified=timestamp,
            **data,
        )
        self.member_repository.create(member=member)
        return member

    def get_all(self, user_id: str, household_id: str) -> Dict[str, Any]:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        response = self.member_repository.get_all(household_id=household_id)
        items = [HouseholdMember.from_dynamo(i) for i in response.get("items", [])]
        return {"items": items}

    def delete(self, user_id: str, household_id: str, member_user_id: str) -> None:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)

        existing = self.member_repository.get(
            household_id=household_id, user_id=member_user_id
        )
        if not existing:
            raise NotFoundError(
                message="Member not found in household",
                resource_type="household_member",
                resource_id=member_user_id,
            )

        self.member_repository.delete(
            household_id=household_id, user_id=member_user_id
        )

