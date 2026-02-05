from enum import Enum


class BlogStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class BlogVisibilityEnum(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class DifficultyEnum(str, Enum):
    EASY = "easy"
    HARD = "hard"
    MEDIUM = "medium"
    TRIVIAL = "trivial"


class HabitCounterEnum(str, Enum):
    DAILY = "daily"
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class HabitStatusEnum(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class HabitTypeEnum(str, Enum):
    BUILD = "build"
    QUIT = "quit"


class HabitEventTypeEnum(str, Enum):
    SUCCESS = "success"
    RESET = "reset"


class HabitEventStatusEnum(str, Enum):
    DONE = "done"
    SKIPPED = "skipped"
    FAILED = "failed"


class ToDoStatusEnum(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DELETED = "deleted"
