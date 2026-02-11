from typing import Any, Dict, Optional
from botocore.exceptions import ClientError

from aws.cognito_service import CognitoService
from models.auth import AuthUser
from models.errors import (
    AuthenticationError,
    UserNotConfirmedError,
    InvalidCredentialsError,
    InvalidConfirmationCodeError,
    CognitoError,
    EmailConflictError,
)
from utils.error_handler import log_error_with_context
from utils.validation import validate_user_profile_data


class AuthService:
    def __init__(self, cognito_service: CognitoService = None):
        self.cognito_service = cognito_service or CognitoService()

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with Cognito.

        Args:
            username: User email
            password: User password

        Returns:
            Authentication tokens

        Raises:
            InvalidCredentialsError: Invalid username/password
            UserNotConfirmedError: User account not confirmed
            CognitoError: Other Cognito errors
        """
        try:
            return self.cognito_service.initiate_auth(
                username=username, password=password
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            log_error_with_context(
                e, operation="cognito_login", username=username, error_code=error_code
            )

            if error_code == "NotAuthorizedException":
                raise InvalidCredentialsError()
            elif error_code == "UserNotConfirmedException":
                raise UserNotConfirmedError(username)
            else:
                raise CognitoError(
                    message=f"Login failed: {error_message}",
                    operation="initiate_auth",
                    original_error=str(e),
                )
        except Exception as e:
            log_error_with_context(e, operation="cognito_login", username=username)
            raise CognitoError(
                message="Unexpected error during login",
                operation="initiate_auth",
                original_error=str(e),
            )

    def signup(
        self,
        email: str,
        password: str,
        phone_number: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        """
        Register new user with Cognito.

        Args:
            email: User email
            password: User password
            phone_number: Optional phone number
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            Signup response from Cognito

        Raises:
            EmailConflictError: Email already exists
            CognitoError: Other Cognito errors
        """
        try:
            # Validate input data
            user_data = {
                "email": email,
                "phone_number": phone_number,
                "first_name": first_name,
                "last_name": last_name,
            }
            # Remove None values
            user_data = {k: v for k, v in user_data.items() if v is not None}
            validate_user_profile_data(user_data)

            return self.cognito_service.sign_up(
                email=email,
                phone_number=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            log_error_with_context(
                e, operation="cognito_signup", email=email, error_code=error_code
            )

            if error_code == "UsernameExistsException":
                raise EmailConflictError(email)
            else:
                raise CognitoError(
                    message=f"Signup failed: {error_message}",
                    operation="sign_up",
                    original_error=str(e),
                )
        except Exception as e:
            log_error_with_context(e, operation="cognito_signup", email=email)
            raise CognitoError(
                message="Unexpected error during signup",
                operation="sign_up",
                original_error=str(e),
            )

    def confirm_signup(self, email: str, confirmation_code: str) -> Dict[str, Any]:
        """
        Confirm user signup with verification code.

        Args:
            email: User email
            confirmation_code: Verification code from email

        Returns:
            Confirmation response from Cognito

        Raises:
            InvalidConfirmationCodeError: Invalid or expired code
            CognitoError: Other Cognito errors
        """
        try:
            return self.cognito_service.confirm_sign_up(email, confirmation_code)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            log_error_with_context(
                e,
                operation="cognito_confirm_signup",
                email=email,
                error_code=error_code,
            )

            if error_code in ["CodeMismatchException", "ExpiredCodeException"]:
                raise InvalidConfirmationCodeError()
            else:
                raise CognitoError(
                    message=f"Confirmation failed: {error_message}",
                    operation="confirm_sign_up",
                    original_error=str(e),
                )
        except Exception as e:
            log_error_with_context(e, operation="cognito_confirm_signup", email=email)
            raise CognitoError(
                message="Unexpected error during confirmation",
                operation="confirm_sign_up",
                original_error=str(e),
            )

    def get_auth_user_from_cognito(self, event: Dict[str, Any]) -> AuthUser:
        response = self.cognito_service.get_user(
            access_token=self.get_access_token(event=event)
        )
        return AuthUser.from_cognito(response)

    @staticmethod
    def get_auth_user_from_claims(event: Dict[str, Any]) -> AuthUser:
        """
        Extract user information from JWT claims.

        Args:
            event: API Gateway event

        Returns:
            AuthUser object

        Raises:
            AuthenticationError: Missing or invalid claims
        """
        try:
            claims = AuthService.get_claims(event)

            user_id = claims.get("sub") or claims.get("username")
            if not user_id:
                raise AuthenticationError("Missing 'sub' claim in JWT")

            return AuthUser(
                user_id=user_id,
                attributes=claims,
            )
        except Exception as e:
            log_error_with_context(e, operation="get_auth_user_from_claims")
            raise AuthenticationError("Failed to extract user from JWT claims")

    @staticmethod
    def get_access_token(event: Dict[str, Any]) -> str:
        """
        Extract access token from Authorization header.

        Args:
            event: API Gateway event

        Returns:
            Access token string

        Raises:
            AuthenticationError: Missing or invalid Authorization header
        """
        headers = event.get("headers") or {}
        auth_header: str = headers.get("authorization") or headers.get("Authorization")

        if not auth_header:
            raise AuthenticationError("Missing Authorization header")

        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]

        return auth_header

    @staticmethod
    def get_claims(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract JWT claims from an API Gateway HTTP API event
        when using a Cognito JWT authorizer.

        Args:
            event: API Gateway event

        Returns:
            JWT claims dictionary

        Raises:
            AuthenticationError: Invalid authorizer context
        """
        try:
            return (
                event.get("requestContext", {})
                .get("authorizer", {})
                .get("jwt", {})
                .get("claims", {})
            ) or {}
        except Exception as e:
            raise AuthenticationError(f"Invalid authorizer context: {e}")

    @staticmethod
    def get_claim(
        event: Dict[str, Any],
        key: str,
        required: bool = False,
    ) -> Optional[str]:
        """
        Get an arbitrary claim from the JWT (e.g. 'email', 'phone_number').

        Args:
            event: API Gateway event
            key: Claim key to retrieve
            required: Whether the claim is required

        Returns:
            Claim value or None

        Raises:
            AuthenticationError: Missing required claim
        """
        claims = AuthService.get_claims(event)
        value = claims.get(key)

        if required and (value is None or value == ""):
            raise AuthenticationError(f"Missing required claim: '{key}'")

        return value
