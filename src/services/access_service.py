from repositories.household_member_repository import HouseholdMemberRepository
from repositories.household_subject_repository import HouseholdSubjectRepository
from utils.errors import ForbiddenError, NotFoundError


class AccessService:
    def __init__(
        self,
        member_repo: HouseholdMemberRepository | None = None,
        subject_repo: HouseholdSubjectRepository | None = None,
    ):
        self.member_repo = member_repo or HouseholdMemberRepository()
        self.subject_repo = subject_repo or HouseholdSubjectRepository()

    def assert_household_member(self, user_id: str, household_id: str) -> None:
        member = self.member_repo.get(household_id=household_id, user_id=user_id)
        if not member:
            raise ForbiddenError("You do not have access to this household")

    def assert_subject_in_household(self, household_id: str, subject_id: str) -> None:
        subject = self.subject_repo.get(
            household_id=household_id, subject_id=subject_id
        )
        if not subject:
            raise NotFoundError("Subject not found")
