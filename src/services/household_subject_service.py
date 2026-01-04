from typing import Any, Dict

from models.household_subject import HouseholdSubject
from repositories.household_subject_repository import HouseholdSubjectRepository
from utils.helper import utc_now_iso


class HouseholdSubjectService:
    def __init__(self, subject_repository: HouseholdSubjectRepository = None):
        self.subject_repo = subject_repository or HouseholdSubjectRepository()

    def create(self, subject_id: str, data: Dict[str, Any]) -> None:
        timestamp = utc_now_iso()
        subject = HouseholdSubject(
            id=subject_id, date_created=timestamp, date_modified=timestamp, **data
        )

        self.subject_repo.create(subject=subject)
