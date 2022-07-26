from src import db
from sqlalchemy.sql import func

class ToDo(db.Model):
    __tablename__ = "to_do"
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(200), nullable=False)
    isCompleted = db.Column(db.Boolean, default=False)
    date_due = db.Column(db.DateTime(timezone=True))
    date_modified = db.Column(db.DateTime(timezone=True), default=func.now())
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)