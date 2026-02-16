from typing import Any, Dict
from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
    DeleteItemInputTableDeleteItemTypeDef,
)

from models.household import Household
from repositories.base_repository import BaseRepository
from utils.helper import utc_now_iso


class HouseholdRepository(BaseRepository):
    def create(self, household: Household) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"HOUSEHOLD#{household.id}",
                "sk": "META#HOUSEHOLD",
                **household.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(self, household_id: str) -> Dict[str, Any] | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {"pk": f"HOUSEHOLD#{household_id}", "sk": "META#HOUSEHOLD"}
        }
        return self.dynamodb_service.get(get_params)

    def update(self, household: Household) -> None:
        household.date_modified = utc_now_iso()
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"HOUSEHOLD#{household.id}",
                "sk": "META#HOUSEHOLD",
                **household.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def delete(self, household_id: str) -> None:
        delete_params: DeleteItemInputTableDeleteItemTypeDef = {
            "Key": {"pk": f"HOUSEHOLD#{household_id}", "sk": "META#HOUSEHOLD"}
        }
        self.dynamodb_service.delete(delete_params)

