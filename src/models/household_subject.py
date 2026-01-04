from dataclasses import dataclass
from typing import Any, Dict

from models.base_model import BaseModel


@dataclass
class HouseholdSubject(BaseModel):
    id: str
    household_id: str
    type: str
    date_created: str
    date_modified: str

    entity: str = "Subject"
    points: float = 0
    level: int = 1
    display_name: str | None = None
    dob: str | None = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        household_id = data.get("household_id")
        if household_id is not None:
            if not isinstance(household_id, str) or not household_id.strip():
                raise ValueError("household_id is required and must be non-empty")

        subject_type = data.get("type")
        if subject_type is not None:
            if not isinstance(subject_type, str) or not subject_type.strip():
                raise ValueError("type is required and must be non-empty")

        return {
            "household_id": household_id,
            "type": subject_type,
            "entity": data.get("entity", "Subject"),
            "display_name": data.get("display_name"),
            "dob": data.get("dob"),
            "points": data.get("points", 0),
            "level": data.get("level", 1),
        }


# SUBJECT == person being tracked
example_subject = {
    "pk": "HOUSEHOLD#<household_id>",
    "sk": "SUBJECT#<subject_id>",
    "entity": "Subject",
    "subject_id": "<subject_id>",
    "household_id": "<household_id>",
    "display_name": "Liz",
    "type": "CHILD",
    "dob": "2024-01-05",
    "points": 0.0,
    "level": 1,
    "date_created": "...",
    "date_modified": "...",
}


# points=(
#     float(item["points"])
#     if isinstance(item["points"], Decimal)
#     else item["points"]
# ),
# level=(
#     int(item["level"])
#     if isinstance(item["level"], Decimal)
#     else item["level"]
# ),
