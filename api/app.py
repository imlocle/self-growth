from flask import Flask
from src.utils.helper import exception_handler
from src.repositories.db_repository import DB_NAME
from src.utils.json_encoder import CustomJSONEncoder

app = Flask(__name__, instance_relative_config=True)
app.config["SECRET_KEY"] = "helloworld"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///src/{DB_NAME}"

# from src.routes.auth import AUTH
# from src.routes.blog import BLOG
from src.routes.habit import HABIT
from src.routes.to_do import TO_DO

# app.register_blueprint(AUTH)
# app.register_blueprint(BLOG)
app.register_blueprint(HABIT)
app.register_blueprint(TO_DO)

# create_database(app)
# Return datetime objects as ISO formatted strings when using JSON encoder.
app.json_encoder = CustomJSONEncoder


@app.errorhandler(Exception)
def error_handler(e):
    return exception_handler(e)


if __name__ == "__main__":
    app.run(debug=True)
