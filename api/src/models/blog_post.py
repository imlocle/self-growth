from src.database.session import BASE
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class BlogPost(BASE):
    __tablename__ = "blog_post"

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    body = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    comments = relationship("Comment", backref="blog_post", passive_deletes=True)
    likes = relationship("Like", backref="blog_post", passive_deletes=True)
    date_published = Column(DateTime(timezone=True))
    date_modified = Column(DateTime(timezone=True), default=func.now())
    date_created = Column(DateTime(timezone=True), default=func.now())


class Comment(BASE):
    id = Column(Integer, primary_key=True)
    text = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    blog_post_id = Column(
        Integer, ForeignKey("blog_post.id", ondelete="CASCADE"), nullable=False
    )
    date_modified = Column(DateTime(timezone=True), default=func.now())
    date_created = Column(DateTime(timezone=True), default=func.now())


class Like(BASE):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    blog_post_id = Column(
        Integer, ForeignKey("blog_post.id", ondelete="CASCADE"), nullable=False
    )
    date_created = Column(DateTime(timezone=True), default=func.now())
