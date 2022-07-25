from api.repository.db_repo import db
from api.blog.blog_post import BlogPost
from api.blog.blog_post_service import BlogPostService
from api.utils.constants import GET, POST
from flask import Blueprint, jsonify, request

blog_blueprint = Blueprint("blog", __name__)

@blog_blueprint.route("/user/<username>/blog-post/create", methods=[POST])
def create_blog_post(username):
    req_data = request.get_json(force=True)
    if req_data:
        blog = BlogPostService.create_blog(req_data)
        return jsonify(blog), 200 if blog else 400


@blog_blueprint.route("/user/<username>/blog-post/delete/<id>")
def delete_blog_post(username, id):
    blog = BlogPost.query.filter_by(id=id).first()
    if blog:
        db.session.delete(blog)
        db.session.commit()
        return jsonify({}), 200

@blog_blueprint.route("/user/<username>/blog-post/list", methods=[GET])
def list_user_blog_post(username):
    blog_service = BlogPostService.list_user_blog_posts(username)
    return jsonify(blog_service), 200
