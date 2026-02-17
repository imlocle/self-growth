from typing import Dict

from mypy_boto3_dynamodb.type_defs import (
    PutItemInputTablePutItemTypeDef,
    GetItemInputTableGetItemTypeDef,
    QueryInputTableQueryTypeDef,
)

from models.blog_post import BlogPost
from repositories.base_repository import BaseRepository
from utils.helper import utc_now_iso


class BlogPostRepository(BaseRepository):
    def create(self, user_id: str, post: BlogPost) -> None:
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_id}",
                "sk": f"BLOG#{post.id}",
                "user_id": user_id,
                **post.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)

    def get(self, user_id: str, post_id: str) -> Dict | None:
        get_params: GetItemInputTableGetItemTypeDef = {
            "Key": {"pk": f"USER#{user_id}", "sk": f"BLOG#{post_id}"}
        }
        return self.dynamodb_service.get(get_params)

    def get_all(self, user_id: str) -> Dict:
        query_params: QueryInputTableQueryTypeDef = {
            "KeyConditionExpression": "#pk = :pk AND begins_with(#sk, :sk)",
            "ExpressionAttributeNames": {"#pk": "pk", "#sk": "sk"},
            "ExpressionAttributeValues": {
                ":pk": f"USER#{user_id}",
                ":sk": "BLOG#",
            },
        }
        return self.dynamodb_service.query(query_params)

    def get_all_paginated(
        self,
        user_id: str,
        limit: int | None = None,
        next_token: dict | None = None,
        filter_expression: str | None = None,
        expression_attr_names: dict | None = None,
        expression_attr_values: dict | None = None,
    ) -> Dict:
        attr_names = {"#pk": "pk", "#sk": "sk"}
        attr_values = {
            ":pk": f"USER#{user_id}",
            ":sk": "BLOG#",
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
            
        return self.dynamodb_service.query(query_params)

    def update(self, user_id: str, post: BlogPost) -> None:
        post.date_modified = utc_now_iso()
        put_params: PutItemInputTablePutItemTypeDef = {
            "Item": {
                "pk": f"USER#{user_id}",
                "sk": f"BLOG#{post.id}",
                "user_id": user_id,
                **post.to_dynamo(),
            }
        }
        self.dynamodb_service.put(put_params)
