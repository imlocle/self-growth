from enum import Enum


class CounterOptionEnum(str, Enum):
    DAILY = "daily"
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class StatusEnum(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    NEW = "new"
    COMPLETED = "completed"


class HabitDifficultyEnum(str, Enum):
    EASY = "easy"
    HARD = "hard"
    MEDIUM = "medium"
    TRIVIAL = "trivial"


class HabitStatusEnum(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class HabitTypeEnum(str, Enum):
    BUILD = "build"
    QUIT = "quit"


class HabitEventTypeEnum(str, Enum):
    SUCCESS = "success"
    RESET = "reset"


class VisibilityEnum(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
