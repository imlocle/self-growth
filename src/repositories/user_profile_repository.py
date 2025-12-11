import os
from typing import Dict

from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
)

from aws.dynamodb_service import DynamodbService
from models.user_profile import UserProfile
from utils.helper import utc_now_iso


class UserProfileRepository:
    def __init__(self, dynamodb_service: DynamodbService = None):
        self.dynamodb_service = dynamodb_service or DynamodbService(
            table_name=os.getenv("SELF_GROWTH_TABLE")
        )

    def create(self, user_profile: UserProfile) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_profile.id}",
                "sk": f"PROFILE",
                **user_profile.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(self, user_id: str) -> Dict | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {"pk": f"USER#{user_id}", "sk": f"PROFILE"}
        }
        return self.dynamodb_service.get(get_params)

    def update(self, user_profile: UserProfile) -> None:
        user_profile.date_modified = utc_now_iso()
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_profile.id}",
                "sk": f"PROFILE",
                **user_profile.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)
