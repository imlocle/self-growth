from typing import Dict, Any, Optional
import json


class BaseError(Exception):
    """Base exception for Self-Growth application"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None,
        http_status: int = 500
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.http_status = http_status
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization"""
        error_dict = {
            "error": self.error_code,
            "message": self.message
        }
        if self.details:
            error_dict["details"] = self.details
        return error_dict
    
    def to_json(self) -> str:
        """Convert error to JSON string"""
        return json.dumps(self.to_dict())


class ValidationError(BaseError):
    """Input validation failed"""
    
    def __init__(
        self, 
        message: str, 
        field: str = None, 
        value: Any = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["provided_value"] = str(value)
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details,
            http_status=400
        )


class AuthorizationError(BaseError):
    """User lacks permission"""
    
    def __init__(
        self, 
        message: str = "Access denied", 
        user_id: str = None,
        resource: str = None,
        action: str = None
    ):
        details = {}
        if user_id:
            details["user_id"] = user_id
        if resource:
            details["resource"] = resource
        if action:
            details["action"] = action
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details,
            http_status=403
        )


class AuthenticationError(BaseError):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            http_status=401
        )


class ConflictError(BaseError):
    """Resource already exists or conflict detected"""
    
    def __init__(
        self, 
        message: str, 
        resource_type: str = None,
        resource_id: str = None,
        conflict_field: str = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        if conflict_field:
            details["conflict_field"] = conflict_field
        
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details=details,
            http_status=409
        )


class NotFoundError(BaseError):
    """Resource not found"""
    
    def __init__(
        self, 
        message: str, 
        resource_type: str = None,
        resource_id: str = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details,
            http_status=404
        )


class BusinessRuleError(BaseError):
    """Business rule violation"""
    
    def __init__(
        self, 
        message: str, 
        rule: str = None,
        context: Dict[str, Any] = None
    ):
        details = context or {}
        if rule:
            details["violated_rule"] = rule
        
        super().__init__(
            message=message,
            error_code="BUSINESS_RULE_ERROR",
            details=details,
            http_status=422
        )


class ExternalServiceError(BaseError):
    """External service (AWS, etc.) error"""
    
    def __init__(
        self, 
        message: str, 
        service: str = None,
        operation: str = None,
        original_error: str = None
    ):
        details = {}
        if service:
            details["service"] = service
        if operation:
            details["operation"] = operation
        if original_error:
            details["original_error"] = original_error
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            http_status=502
        )


class RateLimitError(BaseError):
    """Rate limit exceeded"""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        limit: int = None,
        window: str = None,
        retry_after: int = None
    ):
        details = {}
        if limit:
            details["limit"] = limit
        if window:
            details["window"] = window
        if retry_after:
            details["retry_after_seconds"] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            http_status=429
        )


# Specific domain errors
class HouseholdMembershipError(AuthorizationError):
    """User is not a member of the household"""
    
    def __init__(self, user_id: str, household_id: str):
        super().__init__(
            message=f"User is not a member of household",
            user_id=user_id,
            resource=f"household:{household_id}",
            action="access"
        )


class SubjectNotFoundError(NotFoundError):
    """Subject not found in household"""
    
    def __init__(self, subject_id: str, household_id: str):
        super().__init__(
            message=f"Subject not found in household",
            resource_type="subject",
            resource_id=subject_id
        )
        self.details["household_id"] = household_id


class HabitEventConflictError(ConflictError):
    """Habit event already exists for the period"""
    
    def __init__(self, habit_id: str, period_key: str):
        super().__init__(
            message=f"Habit event already exists for period {period_key}",
            resource_type="habit_event",
            resource_id=f"{habit_id}:{period_key}",
            conflict_field="period_key"
        )


class UsernameConflictError(ConflictError):
    """Username already exists"""
    
    def __init__(self, username: str):
        super().__init__(
            message=f"Username '{username}' is already taken",
            resource_type="user_profile",
            conflict_field="username"
        )


class EmailConflictError(ConflictError):
    """Email already exists"""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"Email '{email}' is already registered",
            resource_type="user_profile",
            conflict_field="email"
        )


# Validation-specific errors
class InvalidUsernameError(ValidationError):
    """Invalid username format"""
    
    def __init__(self, username: str):
        super().__init__(
            message="Username must be 3-20 characters, alphanumeric and underscore only",
            field="username",
            value=username
        )


class InvalidEmailError(ValidationError):
    """Invalid email format"""
    
    def __init__(self, email: str):
        super().__init__(
            message="Invalid email format",
            field="email",
            value=email
        )


class InvalidPhoneError(ValidationError):
    """Invalid phone number format"""
    
    def __init__(self, phone: str):
        super().__init__(
            message="Phone number must be 10-15 digits",
            field="phone_number",
            value=phone
        )


class InvalidEnumError(ValidationError):
    """Invalid enum value"""
    
    def __init__(self, field: str, value: str, valid_values: list):
        super().__init__(
            message=f"Invalid {field}. Must be one of: {', '.join(valid_values)}",
            field=field,
            value=value,
            details={"valid_values": valid_values}
        )


class MissingRequiredFieldError(ValidationError):
    """Required field is missing"""
    
    def __init__(self, field: str):
        super().__init__(
            message=f"Required field '{field}' is missing",
            field=field
        )


# Cognito-specific errors
class CognitoError(ExternalServiceError):
    """Cognito service error"""
    
    def __init__(self, message: str, operation: str, original_error: str = None):
        super().__init__(
            message=message,
            service="cognito",
            operation=operation,
            original_error=original_error
        )


class UserNotConfirmedError(CognitoError):
    """User account not confirmed"""
    
    def __init__(self, email: str):
        super().__init__(
            message="User account not confirmed. Please check your email for confirmation code.",
            operation="login"
        )
        self.details["email"] = email
        self.http_status = 400


class InvalidCredentialsError(CognitoError):
    """Invalid login credentials"""
    
    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            operation="login"
        )
        self.http_status = 401


class InvalidConfirmationCodeError(CognitoError):
    """Invalid confirmation code"""
    
    def __init__(self):
        super().__init__(
            message="Invalid confirmation code",
            operation="confirm_signup"
        )
        self.http_status = 400


# DynamoDB-specific errors
class DynamoDBError(ExternalServiceError):
    """DynamoDB service error"""
    
    def __init__(self, message: str, operation: str, original_error: str = None):
        super().__init__(
            message=message,
            service="dynamodb",
            operation=operation,
            original_error=original_error
        )


class ConditionalCheckFailedError(DynamoDBError):
    """DynamoDB conditional check failed"""
    
    def __init__(self, operation: str, condition: str = None):
        message = "Conditional check failed"
        if condition:
            message += f": {condition}"
        
        super().__init__(
            message=message,
            operation=operation
        )
        self.http_status = 409
