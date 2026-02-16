from typing import Any, Dict

from models.household import Household
from models.errors import NotFoundError
from repositories.household_repository import HouseholdRepository
from services.access_service import AccessService
from utils.helper import utc_now_iso, validate_dict_str_value


class HouseholdService:
    def __init__(
        self,
        household_repository: HouseholdRepository = None,
        access_service: AccessService = None,
    ):
        self.household_repository = household_repository or HouseholdRepository()
        self.access = access_service or AccessService()

    def create(self, user_id: str, household_id: str, data: Dict[str, Any]) -> Household:
        timestamp = utc_now_iso()
        household = Household(
            id=household_id,
            owner_user_id=user_id,
            date_created=timestamp,
            date_modified=timestamp,
            **data,
        )
        self.household_repository.create(household=household)
        return household

    def get(self, user_id: str, household_id: str) -> Household:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        item = self.household_repository.get(household_id)
        if not item:
            raise NotFoundError(
                message="Household not found",
                resource_type="household",
                resource_id=household_id,
            )
        return Household.from_dynamo(item)

    def get_all_for_user(self, user_id: str, member_repo: "HouseholdMemberRepository" = None) -> Dict[str, Any]:
        """
        Get all households for a user by scanning their memberships.
        Uses batch_get to fetch household metadata for each membership.
        """
        from repositories.household_member_repository import HouseholdMemberRepository as MemberRepo
        member_repo = member_repo or MemberRepo()

        # Query GSI or scan for user memberships - for now, use scan with filter
        # In production, a GSI on user_id would be better
        response = self.household_repository.dynamodb_service.scan({
            "FilterExpression": "#sk = :sk AND #uid = :uid",
            "ExpressionAttributeNames": {"#sk": "sk", "#uid": "user_id"},
            "ExpressionAttributeValues": {
                ":sk": f"MEMBER#{user_id}",
                ":uid": user_id,
            },
        })
        membership_items = response.get("items", [])

        households = []
        for membership in membership_items:
            household_id = membership.get("household_id")
            if household_id:
                item = self.household_repository.get(household_id)
                if item:
                    households.append(Household.from_dynamo(item))

        return {"items": households}

    def update(self, user_id: str, household_id: str, data: Dict[str, Any]) -> Household:
        household = self.get(user_id=user_id, household_id=household_id)
        household.name = validate_dict_str_value(data, "name", household.name)
        self.household_repository.update(household=household)
        return household

    def delete(self, user_id: str, household_id: str) -> None:
        self.get(user_id=user_id, household_id=household_id)
        self.household_repository.delete(household_id=household_id)

