from typing import Any, Dict

from models.blog_post import BlogPost
from models.enum import BlogStatusEnum
from repositories.blog_post_repository import BlogPostRepository
from utils.helper import generate_id, parse_enum, utc_now_iso


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

    def get_all(
        self,
        user_id: str,
        limit: int | None = None,
        next_token: dict | None = None,
        status: str | None = None,
    ) -> Dict[str, Any]:
        filter_expr = None
        expr_names = None
        expr_values = None
        if status:
            filter_expr = "#status = :status"
            expr_names = {"#status": "status"}
            expr_values = {":status": status}

        response = self.blog_repo.get_all_paginated(
            user_id=user_id,
            limit=limit,
            next_token=next_token,
            filter_expression=filter_expr,
            expression_attr_names=expr_names,
            expression_attr_values=expr_values,
        )
        return {
            "items": [BlogPost.from_dynamo(i) for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey"),
        }

    def update(self, user_id: str, post_id: str, data: Dict[str, Any]) -> BlogPost:
        blog_post = self.get(user_id=user_id, post_id=post_id)

        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("title must be a non-empty string")
            blog_post.title = title

        if "content" in data:
            content = data["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("content must be a non-empty string")
            blog_post.content = content

        blog_post.summary = data.get("summary", blog_post.summary)

        if "status" in data:
            blog_post.status = parse_enum(BlogStatusEnum, data["status"])

        self.blog_repo.update(user_id=user_id, post=blog_post)
        return blog_post
