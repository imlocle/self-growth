from typing import Any, Dict
from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
)

from models.household_subject import HouseholdSubject
from repositories.base_repository import BaseRepository


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
