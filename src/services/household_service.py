from typing import Any, Dict

from models.household import Household
from repositories.household_repository import HouseholdRepository
from utils.helper import utc_now_iso, validate_dict_str_value


class HouseholdService:
    def __init__(self, household_repository: HouseholdRepository = None):
        self.household_repository = household_repository or HouseholdRepository()

    def create(self, household_id: str, data: Dict[str, Any]):
        timestamp = utc_now_iso()
        household = Household(
            id=household_id, date_created=timestamp, date_modified=timestamp, **data
        )

        self.household_repository.create(household=household)

    def get(self, household_id: str) -> Household:
        item = self.household_repository.get(household_id)
        if not item:
            raise ValueError("Not Found")
        return Household.from_dynamo(item)

    def is_exist(self, household_id: str) -> bool:
        item = self.household_repository.get(household_id)
        if not item:
            return False
        return True

    def update(self, household_id: str, data: Dict[str, Any]):
        household = self.get(household_id=household_id)
        household.name = validate_dict_str_value(data, "name", household.name)

        self.household_repository.update(household=household)
