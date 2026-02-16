from typing import Any, Dict, Optional

from controllers.base_controller import BaseController
from models.blog_post import BlogPost
from services.blog_post_service import BlogPostService


class BlogPostController(BaseController):
    def __init__(
        self, event: Dict[str, Any], blog_service: BlogPostService | None = None
    ):
        super().__init__(event=event, require_auth=True)

        self.blog_service = blog_service or BlogPostService()
        self.post_id = self._get_post_id()

    def _get_post_id(self) -> Optional[str]:
        path = self.event.get("pathParameters") or {}
        return path.get("postId")

    def create(self) -> BlogPost:
        data = BlogPost.from_dict(self.body)
        return self.blog_service.create(self.auth_user.user_id, data)

    def get(self) -> BlogPost:
        return self.blog_service.get(self.auth_user.user_id, self.post_id)

    def get_all(self) -> Dict[str, Any]:
        response = self.blog_service.get_all(self.auth_user.user_id)
        return {
            "items": [i.to_dict() for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey", None),
        }

    def update(self) -> BlogPost:
        return self.blog_service.update(
            user_id=self.auth_user.user_id, post_id=self.post_id, data=self.body
        )
