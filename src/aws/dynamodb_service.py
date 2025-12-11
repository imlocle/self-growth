from typing import Any, Dict, List

import boto3
from mypy_boto3_dynamodb.type_defs import (
    ScanInputTableScanTypeDef,
    GetItemInputTableGetItemTypeDef,
    PutItemInputTablePutItemTypeDef,
    UpdateItemInputTableUpdateItemTypeDef,
    QueryInputTableQueryTypeDef,
    TableAttributeValueTypeDef,
    DeleteItemInputTableDeleteItemTypeDef,
)


class DynamodbService:
    def __init__(self, table_name):
        self.ddb_resource = boto3.resource("dynamodb")
        self.Table = self.ddb_resource.Table(table_name)

    @staticmethod
    def _enhance_request(
        request: Dict[str, Any], default: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        default = default or {}
        return {**default, **request}

    def batch_get(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = []
        response = self.ddb_resource.batch_get_item(**request)
        for table_name, table_items in response.get("Responses", {}).items():
            items.extend(table_items)

        return items

    def get(
        self, request: GetItemInputTableGetItemTypeDef
    ) -> Dict[str, TableAttributeValueTypeDef] | None:
        get_request = self._enhance_request(request, {"ReturnConsumedCapacity": "NONE"})
        response: dict = self.Table.get_item(**get_request)
        return response.get("Item", None)

    def put(
        self, request: PutItemInputTablePutItemTypeDef
    ) -> Dict[str, TableAttributeValueTypeDef] | None:
        response: dict = self.Table.put_item(**request)
        return response.get("ResponseMetadata", None)

    def update(
        self, request: UpdateItemInputTableUpdateItemTypeDef
    ) -> Dict[str, TableAttributeValueTypeDef] | None:
        response: dict = self.Table.update_item(**request)
        return response.get("ResponseMetadata", None)

    def query(self, request: QueryInputTableQueryTypeDef) -> Dict[str, Any]:
        response: dict = self.Table.query(**request)
        return {
            "items": response.get("Items", []),
            "lastEvaluatedKey": response.get("LastEvaluatedKey"),
        }

    def scan(self, request: ScanInputTableScanTypeDef) -> Dict[str, Any]:
        response: dict = self.Table.scan(**request)
        return {
            "items": response.get("Items", []),
            "lastEvaluatedKey": response.get("LastEvaluatedKey"),
        }

    def delete(
        self, request: DeleteItemInputTableDeleteItemTypeDef
    ) -> Dict[str, TableAttributeValueTypeDef]:
        return self.Table.delete_item(**request)
