from sqlalchemy.orm import Session
from src.repositories.blog_repository import BlogRepository
from src.models.blog import BlogSchemaRequest


class BlogService:
    def __init__(self, session: Session) -> None:
        self.repo = BlogRepository(session)

    def create_blog(self, blog_request: BlogSchemaRequest):
        try:
            self.repo.create_blog(blog_request)
        except Exception as e:
            raise e
