"""
Habit event controller for handling habit event requests.
"""

from typing import Any, Dict, Optional

from controllers.base_controller import BaseController
from models.habit_event import HabitEvent
from services.habit_event_service import HabitEventService
from utils.request_context import RequestContext
from utils.validation import validate_habit_event_data


class HabitEventController(BaseController):
    """Controller for habit event operations"""

    def __init__(
        self,
        event: Dict[str, Any],
        request_context: Optional[RequestContext] = None,
        habit_event_service: Optional[HabitEventService] = None,
    ):
        super().__init__(event=event, request_context=request_context, require_auth=True)
        self.habit_event_service = habit_event_service or HabitEventService()
        self._analytics_service = None

    @property
    def period_key(self) -> Optional[str]:
        """Period key from path parameters"""
        return self.path_params.get("periodKey")

    def require_period_key(self) -> str:
        if not self.period_key:
            from models.errors import ValidationError
            raise ValidationError(
                "Missing required path parameter: periodKey", field="periodKey"
            )
        return self.period_key

    def create(self) -> HabitEvent:
        """Create a new habit event"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        habit_id = self.request_context.require_habit_id()
        auth_user = self.request_context.require_auth()

        validated_data = validate_habit_event_data(self.body)

        return self.habit_event_service.create(
            user_id=auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
            data=validated_data,
        )

    def get(self) -> HabitEvent:
        """Get a single habit event by period key"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        habit_id = self.request_context.require_habit_id()
        period_key = self.require_period_key()
        auth_user = self.request_context.require_auth()

        return self.habit_event_service.get(
            user_id=auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
            period_key=period_key,
        )

    def get_all(self) -> Dict[str, Any]:
        """Get all habit events for a habit"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        habit_id = self.request_context.require_habit_id()
        auth_user = self.request_context.require_auth()

        pagination = self.get_pagination_params()

        from utils.helper import decode_next_token, encode_next_token
        next_token = decode_next_token(pagination.get("next_token"))

        response = self.habit_event_service.get_all(
            user_id=auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
            limit=pagination.get("limit"),
            next_token=next_token,
            status=pagination.get("status"),
        )
        return {
            "items": [e.to_dict() for e in response.get("items", [])],
            "nextToken": encode_next_token(response.get("lastEvaluatedKey")),
        }
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics for a habit"""
        from services.habit_analytics_service import HabitAnalyticsService

        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        habit_id = self.request_context.require_habit_id()
        auth_user = self.request_context.require_auth()

        if not self._analytics_service:
            self._analytics_service = HabitAnalyticsService()

        return self._analytics_service.get_analytics(
            user_id=auth_user.user_id,
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
        )
