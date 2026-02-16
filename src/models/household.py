from dataclasses import dataclass
from typing import Any, Dict

from models.base_model import BaseModel


@dataclass
class Household(BaseModel):
    id: str
    name: str
    owner_user_id: str
    date_created: str
    date_modified: str

    entity: str = "Household"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        name = data.get("name")
        if name is not None:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("name is required and must be non-empty")

        owner_user_id = data.get("owner_user_id")
        if owner_user_id is not None:
            if not isinstance(owner_user_id, str) or not owner_user_id.strip():
                raise ValueError("owner_user_id is required and must be non-empty")

        return {
            "name": name,
            "owner_user_id": owner_user_id,
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "Household":
        return cls(
            id=item["id"],
            name=item["name"],
            owner_user_id=item["owner_user_id"],
            entity=item.get("entity", "Household"),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "owner_user_id": self.owner_user_id,
            "entity": self.entity,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }

