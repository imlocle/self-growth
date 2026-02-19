from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, Optional

from models.base_model import BaseModel
from utils.constants import NAME_REGEX, PHONE_REGEX, USERNAME_REGEX


@dataclass
class UserProfile(BaseModel):
    id: str
    username: str
    date_created: str
    date_modified: str

    entity: str = "UserProfile"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate raw profile input. Service assigns:
        - id (Cognito sub)
        - timestamps
        """

        username = data.get("username")
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username is required and must be non-empty")
        if not re.match(USERNAME_REGEX, username):
            raise ValueError(
                "username must be 3-20 characters long and contain only letters, numbers, or underscores"
            )

        first_name = data.get("first_name")
        if first_name is not None:
            if not isinstance(first_name, str) or not first_name.strip():
                raise ValueError("first_name must be non-empty if provided")
            if not re.match(NAME_REGEX, first_name):
                raise ValueError(
                    "first_name may only contain letters, spaces, apostrophes, or hyphens"
                )

        last_name = data.get("last_name")
        if last_name is not None:
            if not isinstance(last_name, str) or not last_name.strip():
                raise ValueError("last_name must be non-empty if provided")
            if not re.match(NAME_REGEX, last_name):
                raise ValueError(
                    "last_name may only contain letters, spaces, apostrophes, or hyphens"
                )

        phone_number = data.get("phone_number")
        if phone_number is not None:
            if not isinstance(phone_number, str) or not phone_number.strip():
                raise ValueError("phone_number must be non-empty if provided")
            if not re.match(PHONE_REGEX, phone_number):
                raise ValueError(
                    "phone_number must contain only digits (with optional +) and be 10-15 characters long"
                )

        return {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "UserProfile":
        return cls(
            id=item["id"],
            username=item["username"],
            first_name=item.get("first_name"),
            last_name=item.get("last_name"),
            phone_number=item.get("phone_number"),
            entity=item.get("entity", "UserProfile"),
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )
    
    # email not included; managed by Cognito
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity": self.entity,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }
