from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
import bcrypt

app = Flask(__name__)
auth = HTTPBasicAuth()

_users = {
    "an@vnu.edu.vn": bcrypt.hashpw(
        b"correct horse battery stable", bcrypt.gensalt()
    )
}

@auth.verify_password
def verify_password(username, password):
    if username not in _users:
        return False;

    stored = _users[username]
    pwd = (password.encode() if isinstance(password, str) else password)

    return username if bcrypt.checkpw(pwd, stored) else None

@auth.error_handler
def on_auth_error(status):
    return jsonify({"error": "unauthorized"}), 401, {
        "WWW-Authenticate": 'Basic realm="orders"'
    }

@app.route("/api/orders", methods=["GET"])
@auth.login_required
def list_orders():
    return jsonify({
        "orders": ["o-001"],
        "princcipal": auth.current_user()
    })

if __name__ == "__main__":
    app.run(ssl_context="adhoc")