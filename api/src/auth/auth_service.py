from src.user.user import User
from src import db

from werkzeug.security import check_password_hash, generate_password_hash


class AuthService:
    def __init__(self) -> None:
        pass
    
    def sign_up(self, data):
        email = data["email"]
        username = data["username"]
        password1 = data["password1"]
        # password2 = request.form.get("password2")

        # email_exists = User.query.filter_by(email=email).first()
        # username_exists = User.query.filter_by(username=username).first()

        # if email_exists:
        #     flash('Email is already in use.', category='error')
        # elif username_exists:
        #     flash('Username is already in use.', category='error')
        # elif password1 != password2:
        #     flash('Password don\'t match!', category='error')
        # elif len(username) < 2:
        #     flash('Username is too short.', category='error')
        # elif len(password1) < 6:
        #     flash('Password is too short.', category='error')
        # elif len(email) < 4:
        #     flash("Email is invalid.", category='error')
        # else:
        new_user = User(email=email, username=username, password=generate_password_hash(
            password1, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        print('User created!')
    
    def login(self, data):
        email = data["email"]
        password = data["password"]
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                return {"message": "login success"}
            else:
                print("error message")
        else:
            print("error message")
