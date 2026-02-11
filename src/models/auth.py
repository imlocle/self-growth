"""
Authentication models for user identity and authorization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AuthUser:
    """
    Authenticated user information.
    
    Can be created from:
    - JWT claims (API Gateway authorizer)
    - Cognito GetUser API response
    """
    
    user_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_claims(cls, claims: Dict[str, Any]) -> Optional["AuthUser"]:
        """
        Create AuthUser from JWT claims (API Gateway authorizer).
        
        Args:
            claims: JWT claims dictionary from API Gateway authorizer
            
        Returns:
            AuthUser instance or None if user_id not found
            
        Example claims structure:
            {
                "sub": "user-uuid",
                "email": "user@example.com",
                "given_name": "John",
                "family_name": "Doe",
                "phone_number": "+1234567890",
                ...
            }
        """
        user_id = claims.get("sub") or claims.get("username")
        if not user_id:
            return None
        
        return cls(
            user_id=user_id,
            email=claims.get("email"),
            first_name=claims.get("given_name"),
            last_name=claims.get("family_name"),
            phone_number=claims.get("phone_number"),
            attributes=claims,
        )

    @classmethod
    def from_cognito(cls, data: Dict[str, Any]) -> "AuthUser":
        """
        Create AuthUser from Cognito GetUser API response.
        
        Args:
            data: Response from cognito_service.get_user()
            
        Returns:
            AuthUser instance
            
        Example data structure:
            {
                "Username": "user-uuid",
                "UserAttributes": [
                    {"Name": "sub", "Value": "user-uuid"},
                    {"Name": "email", "Value": "user@example.com"},
                    {"Name": "given_name", "Value": "John"},
                    {"Name": "family_name", "Value": "Doe"},
                    ...
                ]
            }
        """
        attrs_list = data.get("UserAttributes", [])
        attrs = {a["Name"]: a["Value"] for a in attrs_list}
        
        return cls(
            user_id=attrs.get("sub") or data.get("Username"),
            email=attrs.get("email"),
            first_name=attrs.get("given_name"),
            last_name=attrs.get("family_name"),
            phone_number=attrs.get("phone_number"),
            attributes=attrs,
        )

    @property
    def full_name(self) -> Optional[str]:
        """Get full name (first + last)"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get a custom attribute from the attributes dictionary.
        
        Args:
            key: Attribute key
            default: Default value if key not found
            
        Returns:
            Attribute value or default
        """
        return self.attributes.get(key, default)

    def has_attribute(self, key: str) -> bool:
        """Check if an attribute exists"""
        return key in self.attributes

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for API responses.
        
        Returns:
            Dictionary representation
        """
        return {
            "user_id": self.user_id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "full_name": self.full_name,
        }
