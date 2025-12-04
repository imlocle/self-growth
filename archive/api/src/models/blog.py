from src.database.session import BASE
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class BlogSchemaRequest(DataClassJsonMixin):
    name: str


class BlogTable(BASE):
    __tablename__ = "blog"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    posts = relationship("Post", backref="blog", passive_deletes=True)
    date_modified = Column(DateTime(timezone=True), onupdate=func.now())
    date_created = Column(DateTime(timezone=True), default=func.now())


class PostTable(BASE):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    body = Column(Text, nullable=False)
    blog_id = Column(Integer, ForeignKey("blog.id", ondelete="CASCADE"), nullable=False)
    # user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    comments = relationship("Comment", backref="post", passive_deletes=True)
    likes = relationship("Like", backref="post", passive_deletes=True)
    date_published = Column(DateTime(timezone=True))
    date_modified = Column(DateTime(timezone=True), onupdate=func.now())
    date_created = Column(DateTime(timezone=True), default=func.now())


class CommentTable(BASE):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    text = Column(String(200), nullable=False)
    # user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id", ondelete="CASCADE"), nullable=False)
    date_modified = Column(DateTime(timezone=True), onupdate=func.now())
    date_created = Column(DateTime(timezone=True), default=func.now())


class LikeTable(BASE):
    __tablename__ = "like"

    id = Column(Integer, primary_key=True)
    # user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id", ondelete="CASCADE"), nullable=False)
    date_created = Column(DateTime(timezone=True), default=func.now())
