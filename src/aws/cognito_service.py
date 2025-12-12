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

from models.auth import AuthUser
from utils.errors import AuthError


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
            raise AuthError("Invalid username or password")
        except self.client.exceptions.UserNotFoundException:
            raise AuthError("Invalid username or password")
        except self.client.exceptions.UserNotConfirmedException:
            raise AuthError("User account is not confirmed")
        except ClientError as e:
            raise AuthError("Authentication failed") from e

        auth_result = response.get("AuthenticationResult", {})
        if not auth_result:
            raise AuthError("Authentication failed")

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
            raise AuthError("An account with this email already exists")
        except self.client.exceptions.InvalidPasswordException as e:
            raise AuthError("Password does not meet complexity requirements")
        except self.client.exceptions.InvalidParameterException as e:
            raise AuthError("Invalid signup parameters")
        except ClientError:
            raise AuthError("Signup failed")

        return {
            "user_sub": resp.get("UserSub"),
            "user_confirmed": resp.get("UserConfirmed", False),
            "code_delivery": resp.get("CodeDeliveryDetails", {}),
            "message": "Signup successful. Please confirm the code sent to your email.",
        }

    def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        Fetch user attributes from Cognito using an access token.
        """
        try:
            params: GetUserRequestTypeDef = {"AccessToken": access_token}
            resp = self.client.get_user(**params)
        except self.client.exceptions.NotAuthorizedException:
            raise AuthError("Invalid or expired access token")
        except ClientError as e:
            raise AuthError("Failed to fetch user from Cognito") from e

        return resp
