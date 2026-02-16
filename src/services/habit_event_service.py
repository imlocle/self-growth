from datetime import datetime, timezone

from botocore.exceptions import ClientError

from models.habit_event import HabitEvent
from models.enum import HabitCounterEnum
from repositories.habit_event_repository import HabitEventRepository
from repositories.habit_repository import HabitRepository
from services.access_service import AccessService
from models.errors import NotFoundError
from utils.helper import generate_id, utc_now_iso


class HabitEventService:
    def __init__(
        self,
        event_repo: HabitEventRepository | None = None,
        habit_repo: HabitRepository | None = None,
        access_service: AccessService | None = None,
    ):
        self.event_repo = event_repo or HabitEventRepository()
        self.habit_repo = habit_repo or HabitRepository()
        self.access = access_service or AccessService()

    def create(
        self,
        user_id: str,
        household_id: str,
        subject_id: str,
        habit_id: str,
        data: dict,
    ) -> HabitEvent:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        self.access.assert_subject_in_household(
            household_id=household_id, subject_id=subject_id
        )

        habit_item = self.habit_repo.get(
            household_id=household_id, subject_id=subject_id, habit_id=habit_id
        )
        if not habit_item:
            raise NotFoundError("Habit not found")

        counter = HabitCounterEnum(
            habit_item.get("counter", HabitCounterEnum.DAILY.value)
        )
        period_key = self._period_key(counter=counter)

        now = utc_now_iso()
        event = HabitEvent(
            id=generate_id(),
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
            period_key=period_key,
            date_created=now,
            date_modified=now,
            **data,
        )

        try:
            self.event_repo.create(event)
        except ClientError as e:
            if (
                e.response.get("Error", {}).get("Code")
                == "ConditionalCheckFailedException"
            ):
                raise ValueError("Event already exists for this period") from e
            raise

        return event

    def _period_key(self, counter: HabitCounterEnum) -> str:
        """
        Converts "now" into the period key for daily/weekly/monthly habits.
        Daily:   YYYY-MM-DD
        Weekly:  YYYY-Www (ISO week)
        Monthly: YYYY-MM
        """
        now = datetime.now(timezone.utc)

        if counter == HabitCounterEnum.DAILY:
            return now.strftime("%Y-%m-%d")

        if counter == HabitCounterEnum.WEEKLY:
            year, week, _ = now.isocalendar()
            return f"{year}-W{week:02d}"

        if counter == HabitCounterEnum.MONTHLY:
            return now.strftime("%Y-%m")

        # default fallback
        return now.strftime("%Y-%m-%d")
    def get(
        self,
        user_id: str,
        household_id: str,
        subject_id: str,
        habit_id: str,
        period_key: str,
    ) -> HabitEvent:
        """Get a single habit event by period key."""
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        self.access.assert_subject_in_household(
            household_id=household_id, subject_id=subject_id
        )

        item = self.event_repo.get(
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
            period_key=period_key,
        )
        if not item:
            raise NotFoundError(
                message="Habit event not found",
                resource_type="habit_event",
                resource_id=f"{habit_id}:{period_key}",
            )
        return HabitEvent.from_dynamo(item)

    def get_all(
        self,
        user_id: str,
        household_id: str,
        subject_id: str,
        habit_id: str,
    ) -> dict:
        """Get all habit events for a habit."""
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        self.access.assert_subject_in_household(
            household_id=household_id, subject_id=subject_id
        )

        response = self.event_repo.get_all(
            household_id=household_id,
            subject_id=subject_id,
            habit_id=habit_id,
        )
        items = [HabitEvent.from_dynamo(i) for i in response.get("items", [])]
        return {
            "items": items,
            "lastEvaluatedKey": response.get("lastEvaluatedKey"),
        }


