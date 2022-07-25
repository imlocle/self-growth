from os import path
from flask import Flask
from api.repository.db_repo import DB_NAME, db


def create_api():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "helloworld"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)
    
    from api.auth.auth_route import auth_blueprint
    from api.blog.blog_post_route import blog_blueprint
    from api.habit.habit_route import habit_blueprint
    from api.to_do.to_do_route import to_do_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(blog_blueprint)
    app.register_blueprint(habit_blueprint)
    app.register_blueprint(to_do_blueprint)
    
    create_database(app)

    return app
    

def create_database(app):
    if not path.exists(f"api/{DB_NAME}"):
        db.create_all(app=app)
        print("Created Database!")
