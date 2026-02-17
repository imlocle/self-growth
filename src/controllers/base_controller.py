"""
Base controller class for request parsing and orchestration.
Uses shared RequestContext for context extraction.
"""

from typing import Any, Dict, Optional

from models.auth import AuthUser
from utils.request_context import RequestContext


class BaseController:
    """
    Base class for all controllers.
    
    Uses RequestContext for:
    - Path parameters
    - Query parameters
    - Request body parsing
    - Authentication
    
    The RequestContext can be passed from Handler or created fresh.
    """
    
    def __init__(
        self,
        event: Dict[str, Any],
        request_context: Optional[RequestContext] = None,
        require_auth: bool = True,
    ):
        self.event = event
        
        # Use provided RequestContext or create new one
        # This allows Handler to share context with Controller
        self.request_context = request_context or RequestContext(event)
        
        # Convenience aliases from RequestContext
        self.body = self.request_context.body
        self.household_id = self.request_context.household_id
        self.subject_id = self.request_context.subject_id
        
        # Authentication
        self.auth_user: Optional[AuthUser] = None
        if require_auth:
            self.auth_user = self.request_context.require_auth()
    
    # =========================================================================
    # Convenience Properties (Delegated to RequestContext)
    # =========================================================================
    
    @property
    def user_id(self) -> Optional[str]:
        """User ID from authenticated user"""
        return self.auth_user.user_id if self.auth_user else None
    
    @property
    def query_params(self) -> Dict[str, Any]:
        """Query string parameters"""
        return self.request_context.query_params
    
    @property
    def path_params(self) -> Dict[str, Any]:
        """Path parameters"""
        return self.request_context.path_params
    
    # =========================================================================
    # Require Methods (Delegated to RequestContext)
    # =========================================================================
    
    def require_household_id(self) -> str:
        """Require household ID from path parameters"""
        return self.request_context.require_household_id()
    
    def require_subject_id(self) -> str:
        """Require subject ID from path parameters"""
        return self.request_context.require_subject_id()
    
    # =========================================================================
    # Query Parameter Helpers
    # =========================================================================
    
    def get_query_param(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a query parameter by key"""
        return self.request_context.get_query_param(key, default)
    def get_pagination_params(self) -> Dict[str, Any]:
        """Extract standard pagination and filter params from query string."""
        params: Dict[str, Any] = {}

        limit = self.get_query_param("limit")
        if limit is not None:
            try:
                limit_int = int(limit)
                if limit_int < 1 or limit_int > 100:
                    raise ValueError()
                params["limit"] = limit_int
            except ValueError:
                from models.errors import ValidationError
                raise ValidationError(
                    "limit must be an integer between 1 and 100",
                    field="limit",
                    value=limit,
                )

        next_token = self.get_query_param("nextToken")
        if next_token:
            params["next_token"] = next_token

        status = self.get_query_param("status")
        if status:
            params["status"] = status

        return params
    
    # =========================================================================
    # Error Logging (Delegated to RequestContext)
    # =========================================================================
    
    def log_error(self, error: Exception, operation: str, **additional_context):
        """Log error with full request context"""
        self.request_context.log_error(error, operation, **additional_context)
