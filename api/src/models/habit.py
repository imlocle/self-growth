from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.session import BASE
from dataclasses_json import dataclass_json, config
from dataclasses import dataclass, field
from marshmallow import fields
from marshmallow_enum import EnumField
from typing import List, Optional
from datetime import datetime
from src.models.enum import DifficultyLevelEnum, ResetCounterEnum, StatusEnum


@dataclass_json
@dataclass
class HabitEventsSchemaRequest:
    habit_id: int
    reset_counter: EnumField(ResetCounterEnum, by_value=True)  # type: ignore
    status: EnumField(StatusEnum, by_value=True) = StatusEnum.new.value  # type: ignore
    id: Optional[int] = None


@dataclass_json
@dataclass
class HabitEventsSchemaResponse:
    status: EnumField(StatusEnum, by_value=True)  # type: ignore
    habit_id: int
    reset_counter: EnumField(ResetCounterEnum, by_value=True)  # type: ignore
    date_created: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )
    date_modified: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )
    id: Optional[int] = None


@dataclass_json
@dataclass
class HabitSchemaRequest:
    title: str
    difficulty_level: EnumField(DifficultyLevelEnum, by_value=True)  # type: ignore
    reset_counter: EnumField(ResetCounterEnum, by_value=True)  # type: ignore
    note: str


@dataclass_json
@dataclass
class HabitSchemaResponse:
    id: int
    title: str
    difficulty_level: EnumField(DifficultyLevelEnum, by_value=True)  # type: ignore
    reset_counter: EnumField(ResetCounterEnum, by_value=True)  # type: ignore
    note: str
    habit_events: Optional[List[HabitEventsSchemaResponse]] = None


class HabitTable(BASE):
    __tablename__ = "habit"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    # cues = Column(String(200))
    # current_routine = Column(String(200))
    difficulty_level = Column(Enum(DifficultyLevelEnum))
    reset_counter = Column(Enum(ResetCounterEnum))
    # new_routine = Column(String(200))
    # change_routine = Column(Boolean, default=False)
    # reward = Column(String(200))
    note = Column(Text, default=None)
    # stage = Column(String(100))
    habit_events = relationship(
        "HabitEventsTable", backref="habit", passive_deletes=True
    )
    # user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    date_started = Column(DateTime(timezone=True), default=func.now())
    date_created = Column(DateTime(timezone=True), default=func.now())
    date_modified = Column(DateTime(timezone=True), onupdate=func.now())


class HabitEventsTable(BASE):
    __tablename__ = "habit_events"

    id = Column(Integer, primary_key=True)
    status = Column(Enum(StatusEnum))
    reset_counter = Column(Enum(ResetCounterEnum))
    date_created = Column(DateTime(timezone=True), default=func.now())
    date_modified = Column(DateTime(timezone=True), onupdate=func.now())
    habit_id = Column(
        Integer, ForeignKey("habit.id", ondelete="CASCADE"), nullable=False
    )
