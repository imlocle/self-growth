from enum import Enum


class DifficultyLevelEnum(str, Enum):
    trivial = "trivial"
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ResetCounterEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class StatusEnum(str, Enum):
    new = "new"
    completed = "completed"
