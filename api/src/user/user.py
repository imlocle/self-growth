from src import db
from sqlalchemy.sql import func


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    blog_posts = db.relationship("BlogPost", backref="user", passive_deletes=True)
    comments = db.relationship("Comment", backref="user", passive_deletes=True)
    likes = db.relationship("Like", backref="user", passive_deletes=True)
    habits = db.relationship("Habit", backref="user", passive_deletes=True)
    # pro_cons = db.relationship("ProCon", backref="user", passive_deletes=True)
    to_dos = db.relationship("ToDo", backref="user", passive_deletes=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    date_modified = db.Column(db.DateTime(timezone=True), default=func.now())
