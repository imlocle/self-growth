from flask import Blueprint, jsonify

from src.user.user import User

pro_con_blueprint = Blueprint("pro_con_blueprint", __name__)
# PRO CON SERVICE


@pro_con_blueprint.route("/user/<username>/pro-con/list")
def list_user_pro_cons(username):
    user = User.query.filter_by(username=username).first()
    if user:
        pro_cons = []
        for pc in user.pro_cons:
            pro_cons.append(
                {
                    "id": pc.id,
                    "topic": pc.topic,
                    "pros": pc.pros.split(","),
                    "cons": pc.cons.split(","),
                    "date_created": pc.date_created,
                }
            )
        return jsonify(pro_cons), 200
