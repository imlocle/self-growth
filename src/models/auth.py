from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AuthUser:
    user_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

    @classmethod
    def from_cognito(cls, data: Dict[str, Any]) -> "AuthUser":
        attrs_list = data.get("UserAttributes", [])
        attrs = {a["Name"]: a["Value"] for a in attrs_list}
        return cls(
            user_id=attrs.get("sub"),
            email=attrs.get("email"),
            first_name=attrs.get("given_name"),
            last_name=attrs.get("family_name"),
            attributes=attrs,
        )
