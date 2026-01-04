from typing import Any, Dict
from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
)

from models.household_member import HouseholdMember
from repositories.base_repository import BaseRepository


class HouseholdMemberRepository(BaseRepository):
    def create(self, member: HouseholdMember) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"HOUSEHOLD#{member.household_id}",
                "sk": f"MEMBER#{member.user_id}",
                **member.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(self, household_id: str, user_id: str) -> Dict[str, Any] | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {"pk": f"HOUSEHOLD#{household_id}", "sk": f"MEMBER#{user_id}"}
        }
        return self.dynamodb_service.get(get_params)
