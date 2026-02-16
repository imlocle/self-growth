"""
Auth controller for handling authentication requests.
"""

from typing import Any, Dict

from controllers.base_controller import BaseController
from services.auth_service import AuthService
from utils.request_context import RequestContext
from utils.validation import validate_login_data, validate_signup_data, validate_confirm_signup_data, validate_refresh_token_data


class AuthController(BaseController):
    """Controller for authentication operations"""
    
    def __init__(
        self, 
        event: Dict[str, Any], 
        request_context: RequestContext = None,
        auth_service: AuthService = None
    ):
        super().__init__(event=event, request_context=request_context, require_auth=False)
        self.auth_service = auth_service or AuthService()

    def login(self) -> Dict[str, Any]:
        """
        Perform login via Cognito and return tokens.
        
        Returns:
            Authentication tokens
        """
        # Validate input data in Controller
        validated_data = validate_login_data(self.body)
        
        return self.auth_service.login(
            username=validated_data["username"],
            password=validated_data["password"],
        )

    def signup(self) -> Dict[str, Any]:
        """
        Register new user via Cognito.
        
        Returns:
            Signup response
        """
        # Validate input data in Controller
        validated_data = validate_signup_data(self.body)
        
        return self.auth_service.signup(
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

    def confirm_signup(self) -> Dict[str, Any]:
        """
        Confirm user signup with verification code.
        
        Returns:
            Confirmation response
        """
        # Validate input data in Controller
        validated_data = validate_confirm_signup_data(self.body)
        
        return self.auth_service.confirm_signup(
            email=validated_data["email"], 
            confirmation_code=validated_data["confirmation_code"]
        )
    def refresh_token(self) -> Dict[str, Any]:
        """
        Refresh authentication tokens using refresh token.

        Returns:
            New authentication tokens
        """
        validated_data = validate_refresh_token_data(self.body)

        return self.auth_service.refresh_token(
            refresh_token=validated_data["refresh_token"],
        )


