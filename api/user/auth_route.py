from api import db
from api.user.user import User
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from api.utils.constants import POST

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/login", methods=[POST])
def login():
    req_data = request.get_json(force=True)
    email = req_data["email"]
    password = req_data["password"]
    
    user = User.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            return jsonify({"message": "login success"}), 200
        else:
            print("error message")
    else:
        print("error message")

@auth_blueprint.route("/sign-up", methods=[POST])
def sign_up():
    req_data = request.get_json(force=True)
    email = req_data["email"]
    username = req_data["username"]
    password1 = req_data["password1"]
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
        # return redirect(url_for('views.home'))

    # return render_template("signup.html", user=current_user)

# @auth.route("/logout")
# def logout():
#     logout_user()
#     # return redirect(url_for("views.home"))
