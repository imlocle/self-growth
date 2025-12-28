from typing import Dict

from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
)

from models.user_profile import UserProfile
from repositories.base_repository import BaseRepository
from utils.helper import utc_now_iso


class UserProfileRepository(BaseRepository):
    def create(self, user_profile: UserProfile) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_profile.id}",
                "sk": f"PROFILE#USER",
                **user_profile.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(self, user_id: str) -> Dict | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {"pk": f"USER#{user_id}", "sk": f"PROFILE#USER"}
        }
        return self.dynamodb_service.get(get_params)

    def update(self, user_profile: UserProfile) -> None:
        user_profile.date_modified = utc_now_iso()
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_profile.id}",
                "sk": f"PROFILE#USER",
                **user_profile.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)
