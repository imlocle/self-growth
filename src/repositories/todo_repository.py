from typing import Any, Dict

from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
    QueryInputTableQueryTypeDef,
    DeleteItemInputTableDeleteItemTypeDef,
)

from models.todo import ToDo
from repositories.base_repository import BaseRepository
from utils.helper import utc_now_iso


class ToDoRepository(BaseRepository):
    def create(self, todo: ToDo) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"HOUSEHOLD#{todo.household_id}",
                "sk": f"SUBJECT#{todo.subject_id}#TODO#{todo.id}",
                **todo.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(
        self, household_id: str, subject_id: str, todo_id: str
    ) -> Dict[str, Any] | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {
                "pk": f"HOUSEHOLD#{household_id}",
                "sk": f"SUBJECT#{subject_id}#TODO#{todo_id}",
            }
        }
        return self.dynamodb_service.get(get_params)

    def get_all(self, household_id: str, subject_id: str) -> Dict:
        # TODO Think about querying by status
        query_params: QueryInputTableQueryTypeDef = {
            "KeyConditionExpression": "#pk = :pk AND begins_with(#sk, :sk)",
            # "FilterExpression": "#status = :deleted",
            "ExpressionAttributeNames": {"#pk": "pk", "#sk": "sk"},
            #   "#status": "status"},
            "ExpressionAttributeValues": {
                ":pk": f"HOUSEHOLD#{household_id}",
                ":sk": f"SUBJECT#{subject_id}#TODO#",
                # ":deleted": "deleted",
            },
        }
        return self.dynamodb_service.query(query_params)

    def update(self, todo: ToDo) -> None:
        todo.date_modified = utc_now_iso()
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"HOUSEHOLD#{todo.household_id}",
                "sk": f"SUBJECT#{todo.subject_id}#TODO#{todo.id}",
                **todo.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def delete(self, todo: ToDo) -> Dict:
        delete_params: DeleteItemInputTableDeleteItemTypeDef = {
            "Key": {
                "pk": f"HOUSEHOLD#{todo.household_id}",
                "sk": f"SUBJECT#{todo.subject_id}#TODO#{todo.id}",
            }
        }
        return self.dynamodb_service.delete(delete_params)
