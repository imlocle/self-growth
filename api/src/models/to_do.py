from src.database.session import BASE
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime


class ToDoTable(BASE):
    __tablename__ = "to_do"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    text = Column(Text, default=None)
    isCompleted = Column(Boolean, default=False)
    date_due = Column(DateTime(timezone=True), default=None)
    date_modified = Column(DateTime(timezone=True), default=func.now())
    date_created = Column(DateTime(timezone=True), default=func.now())
    # user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        date_due = (
            datetime.isoformat(self.date_due) if self.date_due is not None else None
        )
        return {
            "id": self.id,
            "title": self.title,
            "isCompleted": self.isCompleted,
            "date_due": date_due,
            "text": self.text,
        }
