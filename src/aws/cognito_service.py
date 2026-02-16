import os
from typing import Any, Dict
import boto3
from botocore.exceptions import ClientError
from mypy_boto3_cognito_idp.client import CognitoIdentityProviderClient
from mypy_boto3_cognito_idp.type_defs import (
    InitiateAuthRequestTypeDef,
    SignUpRequestTypeDef,
    GetUserRequestTypeDef,
)

from models.errors import AuthorizationError


class CognitoService:
    def __init__(self):
        self.client_id = os.getenv("COGNITO_CLIENT_ID")
        self.client: CognitoIdentityProviderClient = boto3.client("cognito-idp")

    def initiate_auth(self, username: str, password: str) -> Dict[str, Any]:
        try:
            params: InitiateAuthRequestTypeDef = {
                "AuthFlow": "USER_PASSWORD_AUTH",
                "AuthParameters": {"USERNAME": username, "PASSWORD": password},
                "ClientId": self.client_id,
            }
            response = self.client.initiate_auth(**params)
        except self.client.exceptions.NotAuthorizedException:
            raise AuthorizationError("Invalid username or password")
        except self.client.exceptions.UserNotFoundException:
            raise AuthorizationError("Invalid username or password")
        except self.client.exceptions.UserNotConfirmedException:
            raise AuthorizationError("User account is not confirmed")
        except ClientError as e:
            raise AuthorizationError("Authentication failed") from e

        auth_result = response.get("AuthenticationResult", {})
        if not auth_result:
            raise AuthorizationError("Authentication failed")

        return {
            "access_token": auth_result.get("AccessToken"),
            "id_token": auth_result.get("IdToken"),
            "refresh_token": auth_result.get("RefreshToken"),
            "expires_tn": auth_result.get("ExpiresIn"),
            "token_type": auth_result.get("TokenType"),
        }

    def sign_up(
        self,
        email: str,
        password: str,
        phone_number: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Dict[str, Any]:
        user_attributes = [
            {"Name": "email", "Value": email},
        ]
        if phone_number:
            user_attributes.append({"Name": "phone_number", "Value": phone_number})
        if first_name:
            user_attributes.append({"Name": "given_name", "Value": first_name})
        if last_name:
            user_attributes.append({"Name": "family_name", "Value": last_name})

        try:
            params: SignUpRequestTypeDef = {
                "ClientId": self.client_id,
                "Username": email,
                "Password": password,
                "UserAttributes": user_attributes,
            }
            resp = self.client.sign_up(**params)
        except self.client.exceptions.UsernameExistsException:
            raise AuthorizationError("An account with this email already exists")
        except self.client.exceptions.InvalidPasswordException as e:
            raise AuthorizationError("Password does not meet complexity requirements")
        except self.client.exceptions.InvalidParameterException as e:
            raise AuthorizationError("Invalid signup parameters")
        except ClientError:
            raise AuthorizationError("Signup failed")

        return {
            "user_sub": resp.get("UserSub"),
            "user_confirmed": resp.get("UserConfirmed", False),
            "code_delivery": resp.get("CodeDeliveryDetails", {}),
            "message": "Signup successful. Please confirm the code sent to your email.",
        }

    def confirm_sign_up(self, email: str, confirmation_code: str) -> Dict[str, Any]:
        """
        Confirm a Cognito user's signup using the emailed confirmation code.
        Public operation; no JWT required.
        """
        try:
            resp = self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code,
            )
        except self.client.exceptions.CodeMismatchException:
            raise AuthorizationError("Invalid confirmation code")
        except self.client.exceptions.ExpiredCodeException:
            raise AuthorizationError("Confirmation code has expired")
        except self.client.exceptions.UserNotFoundException:
            raise AuthorizationError("User not found")
        except self.client.exceptions.NotAuthorizedException:
            raise AuthorizationError("User is already confirmed or cannot be confirmed")
        except ClientError as e:
            raise AuthorizationError("Confirm signup failed") from e
        print(resp)
        return {
            "message": "Signup confirmed. You can now log in.",
        }

    def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user attributes from Cognito using an access token.
        """
        try:
            params: GetUserRequestTypeDef = {"AccessToken": access_token}
            resp = self.client.get_user(**params)
        except self.client.exceptions.NotAuthorizedException:
            raise AuthorizationError("Invalid or expired access token")
        except ClientError as e:
            raise AuthorizationError("Failed to fetch user from Cognito") from e

        return resp
    def refresh_auth(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh authentication tokens using a refresh token.
        """
        try:
            params: InitiateAuthRequestTypeDef = {
                "AuthFlow": "REFRESH_TOKEN_AUTH",
                "AuthParameters": {"REFRESH_TOKEN": refresh_token},
                "ClientId": self.client_id,
            }
            response = self.client.initiate_auth(**params)
        except self.client.exceptions.NotAuthorizedException:
            raise AuthorizationError("Refresh token is invalid or expired")
        except ClientError as e:
            raise AuthorizationError("Token refresh failed") from e

        auth_result = response.get("AuthenticationResult", {})
        if not auth_result:
            raise AuthorizationError("Token refresh failed")

        return {
            "access_token": auth_result.get("AccessToken"),
            "id_token": auth_result.get("IdToken"),
            "expires_in": auth_result.get("ExpiresIn"),
            "token_type": auth_result.get("TokenType"),
        }


