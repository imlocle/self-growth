from src import db
from src.models.blog_post import BlogPost
from src.user.user import User


class BlogPostService:
    def __init__(self) -> None:
        pass

    def create_post(self, data, user_id):
        blog = BlogPost(body=data["body"], title=data["title"], user_id=user_id)
        db.session.add(blog)
        db.session.commit()
        return self.get_blog_by_id(blog.id)

    def get_blog_by_id(self, id):
        return BlogPost.query.filter_by(id=id).first()

    def list_user_blog_posts(self, user_id):
        result = BlogPost.query.filter_by(user_id=user_id)
        if result:
            posts = []
            for post in result:
                posts.append(
                    {
                        "id": post.id,
                        "title": post.title,
                        "body": post.body,
                    }
                )
            return posts
        return []
