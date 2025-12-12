from controllers.blog_post_controller import BlogPostController
from utils.response_util import success_response, error_response


class CreateBlogPostHandler:
    def __init__(self, event):
        self.controller = BlogPostController(event)

    def handler(self):
        try:
            item = self.controller.create()
            return success_response(body=item.to_dict(), status_code=201)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            return error_response()


def lambda_handler(event, context):
    return CreateBlogPostHandler(event).handler()
