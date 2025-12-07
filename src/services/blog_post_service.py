from typing import Any, Dict

from models.blog_post import BlogPost
from models.enum import BlogStatusEnum
from repositories.blog_post_repository import BlogPostRepository
from utils.helper import generate_id, utc_now_iso


class BlogPostService:
    def __init__(self, blog_repo: BlogPostRepository = None):
        self.blog_repo = blog_repo or BlogPostRepository()

    def create(self, user_id: str, data: Dict[str, Any]) -> BlogPost:
        timestamp = utc_now_iso()

        post = BlogPost(
            id=generate_id(),
            date_created=timestamp,
            date_modified=timestamp,
            **data,
        )
        self.blog_repo.create(user_id, post)
        return post

    def get(self, user_id: str, post_id: str) -> BlogPost:
        item = self.blog_repo.get(user_id, post_id)
        if not item:
            raise ValueError("Not Found")
        return BlogPost.from_dynamo(item)

    def get_all(self, user_id: str) -> Dict[str, Any]:
        response = self.blog_repo.get_all(user_id)
        return {
            "items": [BlogPost.from_dynamo(i) for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey"),
        }

    def update(self, user_id: str, post_id: str, data: Dict[str, Any]) -> BlogPost:
        existing = self.blog_repo.get(user_id=user_id, post_id=post_id)
        if not existing:
            raise ValueError("Not Found")

        # Title
        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("title must be a non-empty string")
        else:
            title = existing["title"]

        # Content
        if "content" in data:
            content = data["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("content must be a non-empty string")
        else:
            content = existing["content"]

        # Summary
        summary = data.get("summary", existing.get("summary"))

        # Status
        if "status" in data:
            status_raw = data["status"]
            try:
                status = BlogStatusEnum(status_raw)
            except ValueError:
                raise ValueError(
                    f"Invalid status: '{status_raw}'. "
                    f"Expected one of: {[s.value for s in BlogStatusEnum]}"
                )
        else:
            status = BlogStatusEnum(existing["status"])

        updated_post = BlogPost(
            id=existing["id"],
            title=title,
            content=content,
            summary=summary,
            status=status,
            date_created=existing["date_created"],
            date_modified=utc_now_iso(),
        )

        self.blog_repo.update(user_id=user_id, post=updated_post)
        return updated_post
