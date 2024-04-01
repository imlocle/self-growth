from src.user.user import User


class UserService:
    def __init__(self) -> None:
        pass

    def get_user(self, username):
        return User.query.filter_by(username=username).first()
