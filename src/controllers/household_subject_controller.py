"""
Household subject controller for handling subject requests.
"""

from typing import Any, Dict

from controllers.base_controller import BaseController
from models.household_subject import HouseholdSubject
from services.household_subject_service import HouseholdSubjectService
from utils.helper import generate_id
from utils.request_context import RequestContext
from utils.validation import validate_household_subject_data


class HouseholdSubjectController(BaseController):
    """Controller for household subject operations"""

    def __init__(
        self,
        event: Dict[str, Any],
        request_context: RequestContext = None,
        subject_service: HouseholdSubjectService = None,
    ):
        super().__init__(event=event, request_context=request_context, require_auth=True)
        self.subject_service = subject_service or HouseholdSubjectService()

    def create(self) -> HouseholdSubject:
        """Create a new subject in a household"""
        household_id = self.require_household_id()
        validated_data = validate_household_subject_data(self.body, is_create=True)
        subject_id = generate_id()
        return self.subject_service.create(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            data=validated_data,
        )

    def get(self) -> HouseholdSubject:
        """Get a single subject"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        return self.subject_service.get(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
        )

    def get_all(self) -> Dict[str, Any]:
        """List all subjects in a household"""
        household_id = self.require_household_id()
        response = self.subject_service.get_all(
            user_id=self.user_id, household_id=household_id
        )
        return {
            "items": [s.to_dict() for s in response.get("items", [])],
        }

    def update(self) -> HouseholdSubject:
        """Update a subject"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        validated_data = validate_household_subject_data(self.body, is_create=False)
        return self.subject_service.update(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
            data=validated_data,
        )

    def delete(self) -> None:
        """Delete a subject"""
        household_id = self.require_household_id()
        subject_id = self.require_subject_id()
        self.subject_service.delete(
            user_id=self.user_id,
            household_id=household_id,
            subject_id=subject_id,
        )
