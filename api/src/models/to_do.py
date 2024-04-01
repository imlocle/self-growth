from src.models.enum import StatusEnum
from src.database.session import BASE
from sqlalchemy import (
    Enum,
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from sqlalchemy.sql import func
from dataclasses_json import dataclass_json, config
from dataclasses import dataclass, field
from marshmallow_enum import EnumField
from datetime import datetime
from marshmallow import fields


@dataclass_json
@dataclass
class ToDoSchemaRequest:
    title: str
    text: str
    status: EnumField(StatusEnum, by_value=True)  # type: ignore


@dataclass_json
@dataclass
class ToDoSchemaResponse:
    id: int
    title: str
    text: str
    status: EnumField(StatusEnum, by_value=True)  # type: ignore
    date_due: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )


class ToDoTable(BASE):
    __tablename__ = "to_do"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    status = Column(Enum(StatusEnum))
    text = Column(Text, default=None)
    date_due = Column(DateTime(timezone=True), default=func.now())
    date_modified = Column(DateTime(timezone=True), onupdate=func.now())
    date_created = Column(DateTime(timezone=True), default=func.now())
    # user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
