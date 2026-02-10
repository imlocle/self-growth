from repositories.household_member_repository import HouseholdMemberRepository
from repositories.household_subject_repository import HouseholdSubjectRepository
from models.errors import HouseholdMembershipError, SubjectNotFoundError
from utils.error_handler import log_error_with_context


class AccessService:
    def __init__(
        self,
        member_repo: HouseholdMemberRepository | None = None,
        subject_repo: HouseholdSubjectRepository | None = None,
    ):
        self.member_repo = member_repo or HouseholdMemberRepository()
        self.subject_repo = subject_repo or HouseholdSubjectRepository()

    def assert_household_member(self, user_id: str, household_id: str) -> None:
        """
        Assert that a user is a member of the specified household.
        
        Args:
            user_id: User identifier
            household_id: Household identifier
            
        Raises:
            HouseholdMembershipError: User is not a member of the household
        """
        try:
            member = self.member_repo.get(household_id=household_id, user_id=user_id)
            if not member:
                raise HouseholdMembershipError(user_id, household_id)
        except Exception as e:
            log_error_with_context(
                e,
                user_id=user_id,
                operation="assert_household_member",
                household_id=household_id
            )
            raise

    def assert_subject_in_household(self, household_id: str, subject_id: str) -> None:
        """
        Assert that a subject exists within the specified household.
        
        Args:
            household_id: Household identifier
            subject_id: Subject identifier
            
        Raises:
            SubjectNotFoundError: Subject not found in the household
        """
        try:
            subject = self.subject_repo.get(
                household_id=household_id, subject_id=subject_id
            )
            if not subject:
                raise SubjectNotFoundError(subject_id, household_id)
        except Exception as e:
            log_error_with_context(
                e,
                operation="assert_subject_in_household",
                household_id=household_id,
                subject_id=subject_id
            )
            raise
