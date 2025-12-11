from typing import Any, Dict

from models.blog_post import BlogPost
from services.blog_post_service import BlogPostService
from utils.helper import parse_request_body


class BlogPostController:
    def __init__(self, event: Dict[str, Any], blog_service: BlogPostService = None):
        self.event = event
        # TODO: replace with AuthService + Cognito later
        self.user_id = "1"
        self.blog_service = blog_service or BlogPostService()

    def create(self) -> BlogPost:
        body = parse_request_body(self.event)
        data = BlogPost.from_dict(body)
        return self.blog_service.create(self.user_id, data)

    def get(self) -> BlogPost:
        post_id = self._get_path_params_id()
        return self.blog_service.get(self.user_id, post_id)

    def get_all(self) -> Dict[str, Any]:
        response = self.blog_service.get_all(self.user_id)
        return {
            "items": [i.to_dict() for i in response.get("items")],
            "lastEvaluatedKey": response.get("lastEvaluatedKey", None),
        }

    def update(self) -> BlogPost:
        data = parse_request_body(self.event)
        post_id = self._get_path_params_id()
        return self.blog_service.update(
            user_id=self.user_id, post_id=post_id, data=data
        )

    def _get_path_params_id(self) -> str:
        return self.event.get("pathParameters", {}).get("postId")
