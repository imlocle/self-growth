"""
Auth service for Cognito authentication operations.
"""

from typing import Any, Dict
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


class AuthService:
    """Service for authentication operations with AWS Cognito"""
    
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
    ) -> Dict[str, Any]:
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

    def get_user_from_cognito(self, access_token: str) -> AuthUser:
        """
        Fetch user details from Cognito using access token.
        
        This is used when JWT claims don't contain all needed user attributes
        (e.g., email not in claims but needed for user profile creation).

        Args:
            access_token: Cognito access token

        Returns:
            AuthUser with full user details from Cognito

        Raises:
            CognitoError: If Cognito API call fails
        """
        try:
            response = self.cognito_service.get_user(access_token=access_token)
            return AuthUser.from_cognito(response)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            log_error_with_context(
                e, operation="cognito_get_user", error_code=error_code
            )

            raise CognitoError(
                message=f"Failed to get user from Cognito: {error_message}",
                operation="get_user",
                original_error=str(e),
            )
        except Exception as e:
            log_error_with_context(e, operation="cognito_get_user")
            raise CognitoError(
                message="Unexpected error fetching user from Cognito",
                operation="get_user",
                original_error=str(e),
            )
