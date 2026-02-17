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

    def get_all(
        self,
        household_id: str,
        subject_id: str,
        limit: int | None = None,
        next_token: dict | None = None,
        filter_expression: str | None = None,
        expression_attr_names: dict | None = None,
        expression_attr_values: dict | None = None,
    ) -> Dict:
        # Build base attribute names and values
        attr_names = {"#pk": "pk", "#sk": "sk"}
        attr_values = {
            ":pk": f"HOUSEHOLD#{household_id}",
            ":sk": f"SUBJECT#{subject_id}#TODO#",
        }
        
        # Merge filter attributes if provided
        if expression_attr_names:
            attr_names = {**attr_names, **expression_attr_names}
        if expression_attr_values:
            attr_values = {**attr_values, **expression_attr_values}
        
        query_params: QueryInputTableQueryTypeDef = {
            "KeyConditionExpression": "#pk = :pk AND begins_with(#sk, :sk)",
            "ExpressionAttributeNames": attr_names,
            "ExpressionAttributeValues": attr_values,
        }
        
        if limit:
            query_params["Limit"] = limit
        if next_token:
            query_params["ExclusiveStartKey"] = next_token
        if filter_expression:
            query_params["FilterExpression"] = filter_expression
            
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
