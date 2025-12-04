from flask import Blueprint, jsonify, request
from src.database.session import get_db_session
from src.models.blog import BlogSchemaRequest
from src.repositories.db_repository import DB_PATH
from src.services.blog_service import BlogService

BLOG = Blueprint("BLOG", __name__)
service = BlogService(get_db_session(DB_PATH))


@BLOG.post("/blog/create")
def create_blog():
    blog = BlogSchemaRequest.from_dict(**request.json)
    service.create_blog(blog)
    return jsonify("Created"), 201
