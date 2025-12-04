from sqlalchemy.orm import Session

from src.models.blog import BlogSchemaRequest, BlogTable
from src.repositories.db_repository import DbRepository


class BlogRepository:
    def __init__(self, session: Session) -> None:
        self.db_repo = DbRepository(session)

    def create_blog(self, blog_request: BlogSchemaRequest) -> None:
        self.db_repo.create(BlogTable(**blog_request.to_dict()))
