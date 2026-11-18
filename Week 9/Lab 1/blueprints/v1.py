from flask import Blueprint
from .users_data import get_user

bp = Blueprint("v1", __name__)

@bp.route("/users/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u:
        return {"error": "nf"}, 404
    return {
        "id": uid,
        "fullname": f"{u['f']} {u['l']}",
        "email": u["email"]
    }