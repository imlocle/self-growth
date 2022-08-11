from os import path
from flask import Flask
from src.repository.db_repo import DB_NAME, db


def create_api():

    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = "helloworld"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from src.auth.auth_route import auth_blueprint
    from src.blog.blog_post_route import blog_blueprint
    from src.habit.habit_route import habit_blueprint
    from src.to_do.to_do_route import to_do_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(blog_blueprint)
    app.register_blueprint(habit_blueprint)
    app.register_blueprint(to_do_blueprint)

    create_database(app)

    return app


def create_database(app):
    if not path.exists(f"src/{DB_NAME}"):
        db.create_all(app=app)
        print("Created Database!")
