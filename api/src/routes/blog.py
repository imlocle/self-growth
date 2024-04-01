from src.user.user_service import UserService
from src.repositories.db_repository import db
from src.models.blog_post import BlogPost
from src.services.blog_post_service import BlogPostService
from src.utils.constants import GET, POST
from flask import Blueprint, jsonify, request

BLOG = Blueprint("BLOG", __name__)
service = BlogPostService()
user_service = UserService()


@BLOG.route("/user/<username>/blog-post/create", methods=[POST])
def create(username):
    req_data = request.get_json(force=True)
    user = user_service.get_user(username)
    if user:
        post = service.create_post(req_data, user.id)
        return (
            jsonify({"title": post.title, "body": post.body, "id": post.id}),
            200 if post else 400,
        )


@BLOG.route("/user/<username>/blog-post/delete/<id>")
def delete(username, id):
    blog = BlogPost.query.filter_by(id=id).first()
    if blog:
        db.session.delete(blog)
        db.session.commit()
        return jsonify({}), 200


@BLOG.route("/user/<username>/blog-post/list", methods=[GET])
def list(username):
    user = user_service.get_user(username)
    if user:
        blog_service = service.list_user_blog_posts(user.id)
    return jsonify(blog_service), 200
