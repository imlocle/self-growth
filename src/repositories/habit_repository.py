from typing import Dict

from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
    QueryInputTableQueryTypeDef,
)

from models.habit import Habit
from repositories.base_repository import BaseRepository
from utils.helper import utc_now_iso


class HabitRepository(BaseRepository):
    def create(self, user_id: str, habit: Habit) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_id}",
                "sk": f"HABIT#{habit.id}",
                "user_id": user_id,
                **habit.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(self, user_id: str, habit_id: str) -> Dict | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {"pk": f"USER#{user_id}", "sk": f"HABIT#{habit_id}"}
        }
        return self.dynamodb_service.get(get_params)

    def get_all(self, user_id: str) -> Dict:
        query_params: QueryInputTableQueryTypeDef = {
            "KeyConditionExpression": "#pk = :pk AND begins_with(#sk, :sk)",
            "ExpressionAttributeNames": {"#pk": "pk", "#sk": "sk"},
            "ExpressionAttributeValues": {":pk": f"USER#{user_id}", ":sk": f"HABIT#"},
        }
        return self.dynamodb_service.query(query_params)

    def update(self, user_id: str, habit: Habit) -> None:
        habit.date_modified = utc_now_iso()
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_id}",
                "sk": f"HABIT#{habit.id}",
                "user_id": user_id,
                **habit.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)
