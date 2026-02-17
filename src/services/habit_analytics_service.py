"""
Lightweight habit analytics computed on-the-fly from habit events.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from models.enum import HabitCounterEnum, HabitEventStatusEnum
from models.habit import Habit
from models.habit_event import HabitEvent
from repositories.habit_event_repository import HabitEventRepository
from repositories.habit_repository import HabitRepository
from services.access_service import AccessService
from models.errors import NotFoundError


class HabitAnalyticsService:
    def __init__(
        self,
        event_repo: HabitEventRepository | None = None,
        habit_repo: HabitRepository | None = None,
        access_service: AccessService | None = None,
    ):
        self.event_repo = event_repo or HabitEventRepository()
        self.habit_repo = habit_repo or HabitRepository()
        self.access = access_service or AccessService()

    def get_analytics(
        self,
        user_id: str,
        household_id: str,
        subject_id: str,
        habit_id: str,
    ) -> Dict[str, Any]:
        self.access.assert_household_member(user_id=user_id, household_id=household_id)
        self.access.assert_subject_in_household(
            household_id=household_id, subject_id=subject_id
        )

        habit_item = self.habit_repo.get(
            household_id=household_id, subject_id=subject_id, habit_id=habit_id
        )
        if not habit_item:
            raise NotFoundError("Habit not found")

        habit = Habit.from_dynamo(habit_item)

        response = self.event_repo.get_all(
            household_id=household_id, subject_id=subject_id, habit_id=habit_id
        )
        events = [HabitEvent.from_dynamo(i) for i in response.get("items", [])]

        return self._compute(habit, events)

    def _compute(self, habit: Habit, events: List[HabitEvent]) -> Dict[str, Any]:
        if not events:
            return self._empty_analytics(habit)

        done_keys = sorted(
            e.period_key for e in events if e.status == HabitEventStatusEnum.DONE
        )

        now = datetime.now(timezone.utc)
        total = len(events)
        done = sum(1 for e in events if e.status == HabitEventStatusEnum.DONE)
        skipped = sum(1 for e in events if e.status == HabitEventStatusEnum.SKIPPED)
        failed = sum(1 for e in events if e.status == HabitEventStatusEnum.FAILED)

        current_streak = self._current_streak(done_keys, habit.counter, now)
        longest_streak = self._longest_streak(done_keys, habit.counter)

        return {
            "habit_id": habit.id,
            "counter": habit.counter.value,
            "total_events": total,
            "distribution": {
                "done": done,
                "skipped": skipped,
                "failed": failed,
            },
            "completion_rate": round(done / total, 4) if total > 0 else 0,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "first_event_date": min(e.date_created for e in events),
            "last_event_date": max(e.date_created for e in events),
        }

    def _empty_analytics(self, habit: Habit) -> Dict[str, Any]:
        return {
            "habit_id": habit.id,
            "counter": habit.counter.value,
            "total_events": 0,
            "distribution": {"done": 0, "skipped": 0, "failed": 0},
            "completion_rate": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "first_event_date": None,
            "last_event_date": None,
        }

    def _current_streak(
        self, done_keys: List[str], counter: HabitCounterEnum, now: datetime
    ) -> int:
        """Count consecutive periods ending at the current (or previous) period."""
        if not done_keys:
            return 0

        current_key = self._period_key_for(counter, now)
        prev_key = self._period_key_for(counter, now - self._period_delta(counter))

        # Start from current or previous period
        if done_keys[-1] == current_key or done_keys[-1] == prev_key:
            streak = 0
            check_key = done_keys[-1]
            done_set = set(done_keys)
            dt = self._parse_period_key(counter, check_key)

            while check_key in done_set:
                streak += 1
                dt -= self._period_delta(counter)
                check_key = self._period_key_for(counter, dt)

            return streak

        return 0

    def _longest_streak(self, done_keys: List[str], counter: HabitCounterEnum) -> int:
        if not done_keys:
            return 0

        longest = 1
        current = 1

        for i in range(1, len(done_keys)):
            prev_dt = self._parse_period_key(counter, done_keys[i - 1])
            expected_next = self._period_key_for(
                counter, prev_dt + self._period_delta(counter)
            )

            if done_keys[i] == expected_next:
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest

    def _period_delta(self, counter: HabitCounterEnum) -> timedelta:
        if counter == HabitCounterEnum.DAILY:
            return timedelta(days=1)
        if counter == HabitCounterEnum.WEEKLY:
            return timedelta(weeks=1)
        if counter == HabitCounterEnum.MONTHLY:
            return timedelta(days=30)  # approximate
        return timedelta(days=1)

    def _period_key_for(self, counter: HabitCounterEnum, dt: datetime) -> str:
        if counter == HabitCounterEnum.DAILY:
            return dt.strftime("%Y-%m-%d")
        if counter == HabitCounterEnum.WEEKLY:
            year, week, _ = dt.isocalendar()
            return f"{year}-W{week:02d}"
        if counter == HabitCounterEnum.MONTHLY:
            return dt.strftime("%Y-%m")
        return dt.strftime("%Y-%m-%d")

    def _parse_period_key(self, counter: HabitCounterEnum, key: str) -> datetime:
        if counter == HabitCounterEnum.DAILY:
            return datetime.strptime(key, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if counter == HabitCounterEnum.WEEKLY:
            return datetime.strptime(key + "-1", "%G-W%V-%u").replace(
                tzinfo=timezone.utc
            )
        if counter == HabitCounterEnum.MONTHLY:
            return datetime.strptime(key, "%Y-%m").replace(tzinfo=timezone.utc)
        return datetime.strptime(key, "%Y-%m-%d").replace(tzinfo=timezone.utc)
