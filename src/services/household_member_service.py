from typing import Any, Dict
from models.household_member import HouseholdMember
from repositories.household_member_repository import HouseholdMemberRepository
from utils.helper import utc_now_iso


class HouseholdMemberService:
    def __init__(self, member_repository: HouseholdMemberRepository = None):
        self.member_repository = member_repository or HouseholdMemberRepository()

    def create(self, data: Dict[str, Any]):
        timestamp = utc_now_iso()
        member = HouseholdMember(
            date_created=timestamp, date_modified=timestamp, **data
        )
        self.member_repository.create(member=member)
