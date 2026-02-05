import os
from aws.dynamodb_service import DynamodbService


class BaseRepository:
    def __init__(self, dynamodb_service: DynamodbService | None = None):
        table_name = os.getenv("SELF_GROWTH_TABLE")
        if not table_name:
            raise RuntimeError("SELF_GROWTH_TABLE env var is not set")

        self.dynamodb_service = dynamodb_service or DynamodbService(
            table_name=table_name
        )

    def household_pk(self, household_id: str) -> str:
        return f"HOUSEHOLD#{household_id}"

    def subject_sk(self, subject_id: str) -> str:
        return f"SUBJECT#{subject_id}"
