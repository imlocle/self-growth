import os
from typing import Dict
from aws.dynamodb_service import DynamodbService
from models.to_do import ToDo
from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
    QueryInputTableQueryTypeDef,
)


class ToDoRepository:
    def __init__(self, dynamodb_service: DynamodbService = None):
        self.table_name = os.getenv("SELF_GROWTH_TABLE")
        self.dynamodb_service = dynamodb_service or DynamodbService(
            table_name=self.table_name
        )

    def create(self, user_id: str, todo: ToDo) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_id}",
                "sk": f"TODO#{todo.id}",
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
        query_params: QueryInputTableQueryTypeDef = {
            "KeyConditionExpression": "#pk = :pk",
            "ExpressionAttributeNames": {"#pk": "pk"},
            "ExpressionAttributeValues": {":pk": f"USER#{user_id}"},
        }
        return self.dynamodb_service.query(query_params)

    def update(self, user_id: str, todo: ToDo) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_id}",
                "sk": f"TODO#{todo.id}",
                **todo.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)
