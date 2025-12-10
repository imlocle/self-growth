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


class HabitTypeEnum(str, Enum):
    BUILD = "build"
    QUIT = "quit"


class HabitEventTypeEnum(str, Enum):
    SUCCESS = "success"
    RESET = "reset"


class ToDoStatusEnum(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    COMPLETED = "completed"
