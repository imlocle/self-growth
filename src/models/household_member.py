from dataclasses import dataclass
from typing import Any, Dict

from models.base_model import BaseModel


@dataclass
class HouseholdMember(BaseModel):
    household_id: str
    user_id: str
    role: str
    date_created: str
    date_modified: str

    entity: str = "Member"
    display_name: str | None = None
    dob: str | None = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        household_id = data.get("household_id")
        if household_id is not None:
            if not isinstance(household_id, str) or not household_id.strip():
                raise ValueError("household_id is required and must be non-empty")

        user_id = data.get("user_id")
        if user_id is not None:
            if not isinstance(user_id, str) or not user_id.strip():
                raise ValueError("user_id is required and must be non-empty")

        role = data.get("role")
        if role is not None:
            if not isinstance(role, str) or not role.strip():
                raise ValueError("role is required and must be non-empty")

        return {
            "household_id": household_id,
            "user_id": user_id,
            "role": role,
            "display_name": data.get("display_name"),
            "dob": data.get("dob"),
        }
    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "HouseholdMember":
        return cls(
            household_id=item["household_id"],
            user_id=item["user_id"],
            role=item["role"],
            entity=item.get("entity", "Member"),
            display_name=item.get("display_name"),
            dob=item.get("dob"),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "household_id": self.household_id,
            "user_id": self.user_id,
            "role": self.role,
            "entity": self.entity,
            "display_name": self.display_name,
            "dob": self.dob,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }

