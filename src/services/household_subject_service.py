from typing import Any, Dict

from models.errors import NotFoundError
from models.household_subject import HouseholdSubject
from repositories.household_subject_repository import HouseholdSubjectRepository
from services.access_service import AccessService
from utils.helper import utc_now_iso


class HouseholdSubjectService:
    def __init__(
        self,
        subject_repository: HouseholdSubjectRepository = None,
        access_service: AccessService = None,
    ):
        self.subject_repo = subject_repository or HouseholdSubjectRepository()
        self.access = access_service or AccessService()

    def create(
        self, user_id: str, household_id: str, subject_id: str, data: Dict[str, Any]
    ) -> HouseholdSubject:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        timestamp = utc_now_iso()
        subject = HouseholdSubject(
            id=subject_id,
            household_id=household_id,
            date_created=timestamp,
            date_modified=timestamp,
            **data,
        )
        self.subject_repo.create(subject=subject)
        return subject

    def get(
        self, user_id: str, household_id: str, subject_id: str
    ) -> HouseholdSubject:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        item = self.subject_repo.get(
            household_id=household_id, subject_id=subject_id
        )
        if not item:
            raise NotFoundError(
                message="Subject not found",
                resource_type="subject",
                resource_id=subject_id,
            )
        return HouseholdSubject.from_dynamo(item)

    def get_all(self, user_id: str, household_id: str) -> Dict[str, Any]:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        response = self.subject_repo.get_all(household_id=household_id)
        items = [HouseholdSubject.from_dynamo(i) for i in response.get("items", [])]
        return {"items": items}

    def update(
        self, user_id: str, household_id: str, subject_id: str, data: Dict[str, Any]
    ) -> HouseholdSubject:
        subject = self.get(
            user_id=user_id, household_id=household_id, subject_id=subject_id
        )
        if "display_name" in data:
            subject.display_name = data["display_name"]
        if "type" in data:
            subject.type = data["type"]
        if "dob" in data:
            subject.dob = data["dob"]
        self.subject_repo.update(subject=subject)
        return subject

    def delete(
        self, user_id: str, household_id: str, subject_id: str
    ) -> None:
        self.get(user_id=user_id, household_id=household_id, subject_id=subject_id)
        self.subject_repo.delete(
            household_id=household_id, subject_id=subject_id
        )

