from src import db
from sqlalchemy.sql import func

class ProCon(db.Model):
    __tablename__ = "pro_con"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    pros = db.Column(db.Text, nullable=False)
    cons = db.Column(db.Text, nullable=False)
    date_modified = db.Column(db.DateTime(timezone=True), default=func.now())
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)