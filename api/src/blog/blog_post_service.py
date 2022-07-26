from src.blog.blog_post import BlogPost
from src import db
from src.user.user import User

class BlogPostService:
    def __init__(self) -> None:
        pass
    
    def create_blog(self, data):
        blog = BlogPost(body=data["body"], user_id=data["user_id"])
        db.session.add(blog)
        db.session.commit()
        return self.get_blog_by_id(blog.id)
    
    def get_blog_by_id(self, id):
        return BlogPost.query.filter_by(id=id).first()
    
    def list_user_blog_posts(self, username):
        user = User.query.filter_by(username=username).first()
        posts = []
        for post in user.posts:
            posts.append({
                "id": post.id,
                "title": post.title,
                "body": post.body,
            })
        return posts
