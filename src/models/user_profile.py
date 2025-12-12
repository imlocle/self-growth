from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict

from models.base_model import BaseModel
from utils.constants import EMAIL_REGEX, NAME_REGEX, PHONE_REGEX, USERNAME_REGEX


@dataclass
class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    date_created: str
    date_modified: str

    points: float = 0
    level: int = 1
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate raw user input and return a dict of parsed values.
        The service layer will assign id and timestamps.
        """

        first_name = data.get("first_name")
        if first_name is not None:
            if not isinstance(first_name, str) or not first_name.strip():
                raise ValueError("first name is required and must be non-empty")
            if not re.match(NAME_REGEX, first_name):
                raise ValueError(
                    "first name may only contain letters, spaces, apostrophes, or hyphens"
                )

        last_name = data.get("last_name")
        if last_name is not None:
            if not isinstance(last_name, str) or not last_name.strip():
                raise ValueError("last name is required and must be non-empty")
            if not re.match(NAME_REGEX, last_name):
                raise ValueError(
                    "last name may only contain letters, spaces, apostrophes, or hyphens"
                )

        username = data.get("username")
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username is required and must be non-empty")
        if not re.match(USERNAME_REGEX, username):
            raise ValueError(
                "username must be 3-20 characters long and contain only letters, numbers, or underscores"
            )

        email = data.get("email")
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email is required and must be a non-empty string")
        if not re.match(EMAIL_REGEX, email):
            raise ValueError(f"Invalid Email format: {email}")

        phone_number = data.get("phone_number")
        if phone_number is not None:
            if not isinstance(phone_number, str) or not phone_number.strip():
                raise ValueError("Phone number is required and must be non-empty")
            if not re.match(PHONE_REGEX, phone_number):
                raise ValueError(
                    "Phone number must contain only digits (with optional +) and be 10-15 characters long"
                )

        return {
            "email": email,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "points": data.get("points", 0),
            "level": data.get("level", 1),
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "UserProfile":
        return cls(
            id=item["id"],
            first_name=item["first_name"],
            last_name=item["last_name"],
            username=item["username"],
            email=item["email"],
            phone_number=item["phone_number"],
            points=item["points"],
            level=item["level"],
            date_created=item["date_created"],
            date_modified=item["date_modified"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email,
            "phone_number": self.phone_number,
            "points": self.points,
            "level": self.level,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
        }
