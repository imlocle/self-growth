from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from models.base_model import BaseModel


@dataclass
class HouseholdSubject(BaseModel):
    id: str
    household_id: str
    created_by_user_id: str  # User who created this subject
    type: str
    date_created: str
    date_modified: str

    entity: str = "Subject"

    display_name: Optional[str] = None
    dob: Optional[str] = None  # YYYY-MM-DD

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        household_id = data.get("household_id")
        if not isinstance(household_id, str) or not household_id.strip():
            raise ValueError("household_id is required and must be non-empty")

        subject_type = data.get("type")
        if not isinstance(subject_type, str) or not subject_type.strip():
            raise ValueError("type is required and must be non-empty")

        return {
            "household_id": household_id,
            "type": subject_type,
            "display_name": data.get("display_name"),
            "dob": data.get("dob"),
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "HouseholdSubject":
        return cls(
            id=item["id"],
            household_id=item["household_id"],
            created_by_user_id=item["created_by_user_id"],
            type=item["type"],
            entity=item.get("entity", "Subject"),
            display_name=item.get("display_name"),
            dob=item.get("dob"),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity": self.entity,
            "household_id": self.household_id,
            "created_by_user_id": self.created_by_user_id,
            "type": self.type,
            "display_name": self.display_name,
            "dob": self.dob,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }
