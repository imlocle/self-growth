from api import db
from sqlalchemy.sql import func


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cues = db.Column(db.String(200))
    current_routine = db.Column(db.String(200))
    new_routine = db.Column(db.String(200))
    change_routine = db.Column(db.Boolean, default=False)
    reward = db.Column(db.String(200))
    note = db.Column(db.Text)
    habit_historys = db.relationship("habit_history", backref="habit", passive_deletes=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    date_started = db.Column(db.DateTime(timezone=True), default=func.now())
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    date_modified = db.Column(db.DateTime(timezone=True), default=func.now())

class HabitHistory(db.Model):
    __tablename__ = "habit_history"
    id = db.Column(db.Integer, primary_key=True)
    is_completed = db.Column(db.Boolean)
    date_entry = db.Column(db.DateTime(timezone=True))
    habit_id = db.Column(db.Integer, db.ForeignKey("habit.id", ondelete="CASCADE"), nullable=False)
