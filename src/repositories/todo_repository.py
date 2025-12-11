import os
from typing import Dict

from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
    QueryInputTableQueryTypeDef,
    DeleteItemInputTableDeleteItemTypeDef,
)

from aws.dynamodb_service import DynamodbService
from models.todo import ToDo
from utils.helper import utc_now_iso


class ToDoRepository:
    def __init__(self, dynamodb_service: DynamodbService = None):
        self.dynamodb_service = dynamodb_service or DynamodbService(
            table_name=os.getenv("SELF_GROWTH_TABLE")
        )

    def create(self, user_id: str, todo: ToDo) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_id}",
                "sk": f"TODO#{todo.id}",
                "user_id": user_id,
                **todo.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(self, user_id: str, todo_id: str) -> Dict | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {"pk": f"USER#{user_id}", "sk": f"TODO#{todo_id}"}
        }
        return self.dynamodb_service.get(get_params)

    def get_all(self, user_id: str) -> Dict:
        # TODO Think about querying by status
        query_params: QueryInputTableQueryTypeDef = {
            "KeyConditionExpression": "#pk = :pk AND begins_with(#sk, :sk)",
            # "FilterExpression": "#status = :deleted",
            "ExpressionAttributeNames": {"#pk": "pk", "#sk": "sk"},
            #   "#status": "status"},
            "ExpressionAttributeValues": {
                ":pk": f"USER#{user_id}",
                ":sk": f"TODO#",
                # ":deleted": "deleted",
            },
        }
        return self.dynamodb_service.query(query_params)

    def update(self, user_id: str, todo: ToDo) -> None:
        todo.date_modified = utc_now_iso()
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_id}",
                "sk": f"TODO#{todo.id}",
                "user_id": user_id,
                **todo.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def delete(self, user_id: str, todo_id: str) -> Dict:
        delete_params: DeleteItemInputTableDeleteItemTypeDef = {
            "Key": {"pk": f"USER#{user_id}", "sk": f"TODO#{todo_id}"}
        }
        return self.dynamodb_service.delete(delete_params)
