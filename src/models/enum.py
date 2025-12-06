from enum import Enum


class DifficultyLevelEnum(str, Enum):
    EASY = "easy"
    HARD = "hard"
    MEDIUM = "medium"
    TRIVIAL = "trivial"


class CounterOptionEnum(str, Enum):
    DAILY = "daily"
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class StatusEnum(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    NEW = "new"
    COMPLETED = "completed"


class HabitTypeEnum(str, Enum):
    BUILD = "build"
    QUIT = "quit"


class HabitEventTypeEnum(str, Enum):
    SUCCESS = "success"
    RESET = "reset"


class HabitStatusEnum(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class VisibilityEnum(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
