from typing import Any, Dict
import boto3
from botocore.exceptions import ClientError

from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
    QueryInputTableQueryTypeDef,
)

from models.habit_event import HabitEvent
from repositories.base_repository import BaseRepository
from models.errors import HabitEventConflictError, DynamoDBError
from utils.error_handler import log_error_with_context


class HabitEventRepository(BaseRepository):
    def create(self, event: HabitEvent) -> None:
        """
        One event per period_key enforced via SK.
        
        Raises:
            HabitEventConflictError: If event already exists for this period
            DynamoDBError: For other DynamoDB errors
        """
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": self.household_pk(event.household_id),
                "sk": f"{self.subject_sk(event.subject_id)}#HABIT#{event.habit_id}#EVENT#{event.period_key}",
                "entity": event.entity,
                **event.to_dynamo(),
            },
            # Prevent accidental duplicates for same period
            "ConditionExpression": "attribute_not_exists(#pk) AND attribute_not_exists(#sk)",
            "ExpressionAttributeNames": {"#pk": "pk", "#sk": "sk"},
        }
        
        try:
            self.dynamodb_service.put(put_params)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ConditionalCheckFailedException':
                # Event already exists for this period
                raise HabitEventConflictError(event.habit_id, event.period_key)
            else:
                # Other DynamoDB errors
                log_error_with_context(
                    e,
                    operation="create_habit_event",
                    habit_id=event.habit_id,
                    period_key=event.period_key,
                    error_code=error_code
                )
                raise DynamoDBError(
                    message=f"Failed to create habit event: {e.response['Error']['Message']}",
                    operation="put_item",
                    original_error=str(e)
                )
        except Exception as e:
            log_error_with_context(
                e,
                operation="create_habit_event",
                habit_id=event.habit_id,
                period_key=event.period_key
            )
            raise DynamoDBError(
                message="Unexpected error creating habit event",
                operation="put_item",
                original_error=str(e)
            )

    def get_all(
        self,
        household_id: str,
        subject_id: str,
        habit_id: str,
        limit: int | None = None,
        next_token: dict | None = None,
        filter_expression: str | None = None,
        expression_attr_names: dict | None = None,
        expression_attr_values: dict | None = None,
    ) -> Dict[str, Any]:
        """
        Get all habit events for a specific habit.
        
        Raises:
            DynamoDBError: For DynamoDB query errors
        """
        attr_names = {"#pk": "pk", "#sk": "sk"}
        attr_values = {
            ":pk": self.household_pk(household_id),
            ":sk": f"{self.subject_sk(subject_id)}#HABIT#{habit_id}#EVENT#",
        }
        
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
        
        try:
            return self.dynamodb_service.query(query_params)
        except ClientError as e:
            log_error_with_context(
                e,
                operation="get_all_habit_events",
                household_id=household_id,
                subject_id=subject_id,
                habit_id=habit_id,
                error_code=e.response['Error']['Code']
            )
            raise DynamoDBError(
                message=f"Failed to query habit events: {e.response['Error']['Message']}",
                operation="query",
                original_error=str(e)
            )
        except Exception as e:
            log_error_with_context(
                e,
                operation="get_all_habit_events",
                household_id=household_id,
                subject_id=subject_id,
                habit_id=habit_id
            )
            raise DynamoDBError(
                message="Unexpected error querying habit events",
                operation="query",
                original_error=str(e)
            )
    def get(
        self, household_id: str, subject_id: str, habit_id: str, period_key: str
    ) -> Dict[str, Any] | None:
        """Get a single habit event by period key."""
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {
                "pk": self.household_pk(household_id),
                "sk": f"{self.subject_sk(subject_id)}#HABIT#{habit_id}#EVENT#{period_key}",
            }
        }
        return self.dynamodb_service.get(get_params)


