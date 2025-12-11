import os
from typing import Any, Dict
import boto3
from botocore.exceptions import ClientError

from utils.errors import AuthError


class CognitoService:
    def __init__(self):
        self.client_id = os.getenv("COGNITO_CLIENT_ID")
        self.client = boto3.client("cognito-idp", region_name="us-west-1")

    def initiate_auth(self, username: str, password: str) -> Dict[str, Any]:
        try:
            response = self.client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": username,
                    "PASSWORD": password,
                },
                ClientId=self.client_id,
            )
        except self.client.exceptions.NotAuthorizedException:
            raise AuthError("Invalid username or password")
        except self.client.exceptions.UserNotFoundException:
            raise AuthError("Invalid username or password")
        except self.client.exceptions.UserNotConfirmedException:
            raise AuthError("User account is not confirmed")
        except ClientError as e:
            # Log details in CloudWatch, but don’t leak internal info to client
            raise AuthError("Authentication failed") from e

        auth_result = response.get("AuthenticationResult", {})
        if not auth_result:
            raise AuthError("Authentication failed")

        return {
            "accessToken": auth_result.get("AccessToken"),
            "idToken": auth_result.get("IdToken"),
            "refreshToken": auth_result.get("RefreshToken"),
            "expiresIn": auth_result.get("ExpiresIn"),
            "tokenType": auth_result.get("TokenType"),
        }
