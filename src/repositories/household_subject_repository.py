from typing import Any, Dict
from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
    QueryInputTableQueryTypeDef,
    DeleteItemInputTableDeleteItemTypeDef,
)

from models.household_subject import HouseholdSubject
from repositories.base_repository import BaseRepository
from utils.helper import utc_now_iso


class HouseholdSubjectRepository(BaseRepository):
    def create(self, subject: HouseholdSubject) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"HOUSEHOLD#{subject.household_id}",
                "sk": f"SUBJECT#{subject.id}",
                **subject.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(self, household_id: str, subject_id: str) -> Dict[str, Any] | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {"pk": f"HOUSEHOLD#{household_id}", "sk": f"SUBJECT#{subject_id}"}
        }
        return self.dynamodb_service.get(get_params)

    def get_all(self, household_id: str) -> Dict:
        query_params: QueryInputTableQueryTypeDef = {
            "KeyConditionExpression": "#pk = :pk AND begins_with(#sk, :sk)",
            "ExpressionAttributeNames": {"#pk": "pk", "#sk": "sk"},
            "ExpressionAttributeValues": {
                ":pk": f"HOUSEHOLD#{household_id}",
                ":sk": "SUBJECT#",
            },
        }
        return self.dynamodb_service.query(query_params)

    def update(self, subject: HouseholdSubject) -> None:
        subject.date_modified = utc_now_iso()
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"HOUSEHOLD#{subject.household_id}",
                "sk": f"SUBJECT#{subject.id}",
                **subject.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def delete(self, household_id: str, subject_id: str) -> None:
        delete_params: DeleteItemInputTableDeleteItemTypeDef = {
            "Key": {"pk": f"HOUSEHOLD#{household_id}", "sk": f"SUBJECT#{subject_id}"}
        }
        self.dynamodb_service.delete(delete_params)

