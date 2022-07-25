from sqlalchemy.sql import func
from api import db

class BlogPost(db.Model):
    __tablename = "blog_post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='blog_post', passive_deletes=True)
    likes = db.relationship('Like', backref='blog_post', passive_deletes=True)
    date_published = db.Column(db.DateTime(timezone=True))
    date_modified = db.Column(db.DateTime(timezone=True), default=func.now())
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    blog_post_id = db.Column(db.Integer, db.ForeignKey(
        'blog_post.id', ondelete="CASCADE"), nullable=False)
    date_modified = db.Column(db.DateTime(timezone=True), default=func.now())
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    blog_post_id = db.Column(db.Integer, db.ForeignKey(
        'blog_post.id', ondelete="CASCADE"), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())